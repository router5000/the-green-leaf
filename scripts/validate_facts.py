#!/usr/bin/env python3
"""Blocking fact-verification gate for articles and strain profiles.

An item may auto-publish ONLY if `validate()` returns passed=True. Rules:

  citations   every cited URL is a deep link (not a bare homepage), returns
              HTTP 200, and (when a research bundle is given) belongs to the
              research set the article was written from.
  claims      every numeric / award / lineage claim maps to a snippet in the
              fetched sources (string + number match), and an independent model
              (claude-haiku, never the generator's model) confirms the snippet
              supports the claim.
  thc         any THC % must be phrased as "reported" and carry a citation.
  medical     no medical-claim language (treats, cures, relieves pain, ...).
  awards      award / cup claims need a citation link in the same sentence.
  law         law/legality pages need >= 1 .gov citation and a
              "Last checked: YYYY-MM-DD" date.

CLI:
  python scripts/validate_facts.py drafts/json/<slug>.json --research research/<slug>.json
  python scripts/validate_facts.py site/content/posts/<slug>.md          # re-check
Exit code 0 = pass, 1 = fail.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

import requests

SUPPORT_MODEL = os.getenv("FACTCHECK_MODEL", "claude-haiku-4-5-20251001")
GENERATOR_MODEL = "claude-sonnet-4-6"
USER_AGENT = "Mozilla/5.0 (compatible; StrainReportFactCheck/1.0; +https://strainreport.com)"

MEDICAL_TERMS = [
    r"\bcures?\b", r"\bcured\b", r"\btreats?\b", r"\btreating\b", r"\btreatment (?:for|of)\b",
    r"\bheals?\b", r"\bremed(?:y|ies) for\b", r"\brelie(?:f|ves?) (?:from )?(?:pain|anxiety|depression|insomnia|stress|nausea|inflammation|migraines?|seizures?)\b",
    r"\bpain relief\b", r"\banti-?inflammatory\b", r"\btherapeutic\b", r"\bmedical (?:benefits?|uses?)\b",
    r"\b(?:helps?|good|great|ideal|best) (?:with|for) (?:pain|anxiety|depression|insomnia|ptsd|nausea|migraines?|seizures?|arthritis|cancer|epilepsy|chronic pain)\b",
    r"\b(?:patients|prescrib\w*)\b", r"\bdepression relief\b",
]
# Phrases that legitimately contain a medical term in a disclaimer.
MEDICAL_ALLOW = [r"not (?:a )?medical advice", r"do(?:es)? not (?:make|offer) medical claims",
                 r"consult (?:a|your) (?:doctor|physician|healthcare)", r"not intended to (?:diagnose|treat)"]

AWARD_RE = re.compile(r"\b(cannabis cup|emerald cup|cannabis crown|zalympix|sippi cup|copa \w+|award|awards|winner|won|1st place|2nd place|3rd place|first place|second place|third place|top ten|strain of the year)\b", re.I)
LINEAGE_RE = re.compile(r"(\bcross(?:ed|ing)? (?:of|between|with)\b|\blineage\b|\bparents?\b|\bbred from\b|\b[A-Z][\w#']+(?: [A-Z#\d][\w#']*)* (?:x|×) [A-Z][\w#']+)")
NUM_RE = re.compile(r"(?<![\w#/.-])(\d{1,4}(?:\.\d+)?)\s*(%|percent|µm|micron|microns|mg|hours?|minutes?|weeks?|days?)?")
PCT_RE = re.compile(r"\d{1,2}(?:\.\d+)?\s*(?:%|percent)")
THC_PCT_RE = re.compile(r"THC[^.]{0,60}?\d{1,2}(?:\.\d+)?\s*(?:%|percent)|\d{1,2}(?:\.\d+)?\s*(?:%|percent)[^.]{0,20}?THC", re.I)
CITE_RE = re.compile(r"\[\[(\d+)\]\]\(#user-content-fn-\d+\)|\[(\d+)\]")
LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")
LAW_TOPIC_RE = re.compile(r"\b(legal|legality|law|laws|legaliz\w*|possession limits?|penalt\w+|tsa|fly(?:ing)? with|travel(?:ing)? with)\b", re.I)
LAST_CHECKED_RE = re.compile(r"last (?:checked|verified|reviewed)[:\s]+(\d{4}-\d{2}-\d{2})", re.I)
YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")

UrlChecker = Callable[[str], int]
SupportChecker = Callable[[list[dict]], list[dict]]


@dataclass
class Issue:
    rule: str
    detail: str
    claim: str = ""


@dataclass
class Result:
    passed: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    claims_checked: int = 0
    urls_checked: int = 0

    def fail(self, rule, detail, claim=""):
        self.passed = False
        self.errors.append(asdict(Issue(rule, detail, claim[:300])))

    def warn(self, rule, detail, claim=""):
        self.warnings.append(asdict(Issue(rule, detail, claim[:300])))

    def to_dict(self):
        return asdict(self)


# ── parsing ──────────────────────────────────────────────────────────────────

def load_article(path: Path) -> dict:
    """Accepts drafts/json/<slug>.json or a .md with YAML frontmatter."""
    path = Path(path)
    if path.suffix == ".json":
        return json.loads(path.read_text())
    import yaml
    raw = path.read_text(encoding="utf-8")
    fm, body = {}, raw
    if raw.startswith("---"):
        _, fm_txt, body = raw.split("---", 2)
        fm = yaml.safe_load(fm_txt) or {}
    fm["content"] = body
    fm.setdefault("slug", path.stem)
    return fm


def split_sources_section(content: str) -> tuple[str, str]:
    m = re.search(r"^##\s+(?:Sources|References)\s*$", content, re.M | re.I)
    if not m:
        return content, ""
    return content[: m.start()], content[m.end():]


def numbered_sources(sources_md: str) -> dict[int, str]:
    out = {}
    for line in sources_md.splitlines():
        m = re.match(r"\s*(\d+)\.\s+.*?\((https?://[^)\s]+)\)", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def is_bare_homepage(url: str) -> bool:
    p = urlparse(url)
    path = (p.path or "/").rstrip("/")
    return path == "" and not p.query


def sentences(text: str) -> list[str]:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)       # images
    text = re.sub(r"<[^>]+>", " ", text)                       # html anchors
    text = re.sub(r"^\s*\|?\s*-{3,}.*$", " ", text, flags=re.M)  # table rules
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\[*])|\n+", text)
    return [p.strip(" -*#|\t") for p in parts if len(p.strip()) > 3]


def is_internal_or_ignorable(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return (host.endswith("strainreport.com") or "amazon." in host or "amzn." in host
            or "youtube.com" in host or "youtu.be" in host)


# ── claim detection ──────────────────────────────────────────────────────────

def claim_kinds(sentence: str) -> set[str]:
    kinds = set()
    stripped = CITE_RE.sub("", sentence)
    if THC_PCT_RE.search(stripped):
        kinds.add("thc")
    if PCT_RE.search(stripped) or re.search(r"\b\d+(?:\.\d+)?\s*(?:µm|microns?|mg)\b", stripped) or YEAR_RE.search(stripped):
        kinds.add("numeric")
    if AWARD_RE.search(stripped) and (YEAR_RE.search(stripped) or re.search(r"cup|crown|zalympix|award", stripped, re.I)):
        kinds.add("award")
    if LINEAGE_RE.search(stripped):
        kinds.add("lineage")
    return kinds


def claim_tokens(sentence: str) -> dict:
    s = CITE_RE.sub("", sentence)
    s = LINK_RE.sub(r"\1", s)
    nums = [n for n, _ in NUM_RE.findall(s)]
    years = YEAR_RE.findall(s)
    names = re.findall(r"\b([A-Z][a-zA-Z#']+(?:\s+(?:[A-Z#\d][\w#']*))*)", s)
    return {"numbers": sorted(set(nums)), "years": sorted(set(years)), "names": names}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


def _num_in(text: str, n: str) -> bool:
    return re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", text) is not None


def find_snippet(sentence: str, kinds: set[str], source_texts: dict[str, str]) -> Optional[dict]:
    """Deterministic match: a source window must contain every number in the
    claim; award claims also need the year; lineage claims need both names."""
    tok = claim_tokens(sentence)
    nums = tok["numbers"]
    best = None
    for url, text in source_texts.items():
        low = _norm(text)
        if nums and not all(_num_in(low, n) for n in nums):
            continue
        anchor = nums[0] if nums else None
        idxs = [m.start() for m in re.finditer(rf"(?<![\d.]){re.escape(anchor)}(?!\d)", low)] if anchor else [0]
        for i in idxs[:20]:
            window = low[max(0, i - 400): i + 400]
            if nums and not all(_num_in(window, n) for n in nums):
                continue
            if "lineage" in kinds:
                parents = [n.lower() for n in tok["names"] if len(n) > 2][:4]
                hits = sum(1 for n in parents if n in low)
                if parents and hits < min(2, len(parents)):
                    continue
            if "award" in kinds and not re.search(r"cup|crown|award|zalympix|place|winner|won", window):
                continue
            cand = {"url": url, "snippet": text_window(text, window)}
            if best is None:
                best = cand
            break
        if best:
            break
    return best


def text_window(original: str, window_lower: str) -> str:
    return window_lower[:800]


# ── network checks (injectable for tests) ────────────────────────────────────

_url_cache: dict[str, int] = {}


def http_status(url: str) -> int:
    if url in _url_cache:
        return _url_cache[url]
    try:
        r = requests.head(url, headers={"User-Agent": USER_AGENT}, timeout=15, allow_redirects=True)
        code = r.status_code
        if code in (403, 405, 429) or code >= 500:
            r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20, allow_redirects=True, stream=True)
            code = r.status_code
            r.close()
    except Exception:
        code = 0
    _url_cache[url] = code
    return code


def model_support_check(items: list[dict]) -> list[dict]:
    """Ask an independent model whether each snippet supports each claim.
    Returns [{"supported": bool, "reason": str}] aligned with items. Raises if
    no API key so callers can decide fail-open vs fail-closed."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    if SUPPORT_MODEL == GENERATOR_MODEL:
        raise RuntimeError("support model must differ from the generator model")
    import anthropic
    client = anthropic.Anthropic()
    out = []
    for chunk_start in range(0, len(items), 15):
        chunk = items[chunk_start: chunk_start + 15]
        listing = "\n\n".join(
            f"#{i}\nCLAIM: {it['claim']}\nSOURCE ({it['url']}): {it['snippet']}" for i, it in enumerate(chunk))
        prompt = (
            "You are a strict fact checker. For each numbered item decide whether the SOURCE text, "
            "and only the source text, directly supports every factual detail of the CLAIM (numbers, "
            "years, award names, placements, parent strains). Ignore style. If the claim adds any "
            "detail not in the source, it is NOT supported.\n\n" + listing +
            '\n\nReturn ONLY JSON: [{"i": 0, "supported": true|false, "reason": "short"}]'
        )
        msg = client.messages.create(model=SUPPORT_MODEL, max_tokens=1500, timeout=90,
                                     messages=[{"role": "user", "content": prompt}])
        raw = msg.content[0].text
        data = json.loads(raw[raw.find("["): raw.rfind("]") + 1])
        by_i = {d.get("i"): d for d in data if isinstance(d, dict)}
        for i in range(len(chunk)):
            d = by_i.get(i, {"supported": False, "reason": "no verdict returned"})
            out.append({"supported": bool(d.get("supported")), "reason": str(d.get("reason", ""))[:200]})
    return out


# ── main validation ──────────────────────────────────────────────────────────

def validate(article: dict, bundle: Optional[dict] = None, *,
             url_checker: UrlChecker = http_status,
             support_checker: Optional[SupportChecker] = model_support_check,
             require_model: bool = True,
             fetch_cited: Optional[Callable[[str], str]] = None) -> Result:
    res = Result()
    content = article.get("content", "") or ""
    body, sources_md = split_sources_section(content)
    numbered = numbered_sources(sources_md)
    keyword = f"{article.get('keyword', '')} {article.get('title', '')}"

    # 1. citations
    cited = list(dict.fromkeys(list(numbered.values()) +
                               [u for _, u in LINK_RE.findall(body) if not is_internal_or_ignorable(u)]))
    if not numbered:
        res.fail("citations", "no numbered ## Sources section")
    bundle_urls = {s["url"].rstrip("/") for s in (bundle or {}).get("sources", [])}
    for url in cited:
        res.urls_checked += 1
        if is_bare_homepage(url):
            res.fail("citations", f"bare homepage cited: {url}")
            continue
        code = url_checker(url)
        if code != 200:
            res.fail("citations", f"cited URL returned {code}: {url}")
        if bundle is not None and url.rstrip("/") not in bundle_urls:
            res.fail("citations", f"cited URL not in research set: {url}")
    for n in {int(a or b) for a, b in CITE_RE.findall(body)}:
        if numbered and n not in numbered:
            res.fail("citations", f"citation [{n}] has no matching source")

    # Source texts available for claim matching.
    source_texts: dict[str, str] = {}
    for s in (bundle or {}).get("sources", []):
        source_texts[s["url"]] = s.get("text", "")
    if fetch_cited:
        for url in numbered.values():
            if url not in source_texts:
                try:
                    source_texts[url] = fetch_cited(url)
                except Exception:
                    pass

    # 2. collect claim-bearing text (body + structured fields that render on page)
    texts = [("body", s) for s in sentences(body)]
    for k in ("key_stat", "tldr", "meta_description", "title"):
        if article.get(k):
            texts += [(k, s) for s in sentences(str(article[k]))]
    for faq in article.get("faqs") or []:
        texts += [("faq", s) for s in sentences(str(faq.get("answer", "")))]

    to_model = []
    for where, sent in texts:
        plain = CITE_RE.sub("", sent)
        if LAST_CHECKED_RE.search(plain):
            continue
        # medical language
        if not any(re.search(a, plain, re.I) for a in MEDICAL_ALLOW):
            for pat in MEDICAL_TERMS:
                if re.search(pat, plain, re.I):
                    res.fail("medical", f"medical-claim language ({where})", sent)
                    break
        kinds = claim_kinds(sent)
        if not kinds:
            continue
        res.claims_checked += 1
        has_cite = bool(CITE_RE.search(sent)) or bool(LINK_RE.search(sent))
        if "thc" in kinds:
            if not re.search(r"\breported\b|\breports\b|\blists?\b|\bshows?\b", plain, re.I):
                res.fail("thc", f"THC % not phrased as reported ({where})", sent)
            if where == "body" and not has_cite:
                res.fail("thc", "THC % without a citation", sent)
        if "award" in kinds and where == "body" and not has_cite:
            res.fail("awards", "award claim without a citation link", sent)
        if kinds & {"numeric", "award", "lineage", "thc"}:
            snip = find_snippet(sent, kinds, source_texts) if source_texts else None
            if not snip:
                res.fail("unsupported", f"no source snippet supports this {'/'.join(sorted(kinds))} claim ({where})", sent)
            else:
                to_model.append({"claim": plain, "url": snip["url"], "snippet": snip["snippet"], "where": where})

    # 3. independent model support check
    if to_model:
        if support_checker is None:
            if require_model:
                res.fail("model_check", "independent model check required but disabled")
        else:
            try:
                verdicts = support_checker(to_model)
                for it, v in zip(to_model, verdicts):
                    if not v["supported"]:
                        res.fail("unsupported", f"model: not supported by {it['url']} ({v['reason']})", it["claim"])
            except Exception as e:
                if require_model:
                    res.fail("model_check", f"independent model check unavailable: {e}")
                else:
                    res.warn("model_check", f"skipped: {e}")

    # 4. law pages
    if LAW_TOPIC_RE.search(keyword) or article.get("category") in ("laws", "legal", "state-laws"):
        if not any(urlparse(u).netloc.lower().endswith(".gov") for u in cited):
            res.fail("law", "law/legality page without a .gov source")
        if not (LAST_CHECKED_RE.search(content) or article.get("last_checked")):
            res.fail("law", "law/legality page without a 'Last checked: YYYY-MM-DD' date")
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article", help="drafts/json/<slug>.json or a .md post")
    ap.add_argument("--research", help="research/<slug>.json bundle")
    ap.add_argument("--fetch-cited", action="store_true",
                    help="fetch cited pages to use as source text (for re-checking published posts)")
    ap.add_argument("--no-model", action="store_true", help="skip the model check (local debugging only; result is a FAIL)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    article = load_article(Path(a.article))
    bundle = json.loads(Path(a.research).read_text()) if a.research else None
    fetch = None
    if a.fetch_cited:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from research import fetch_source
        fetch = lambda u: fetch_source(u, "cited").text  # noqa: E731
    r = validate(article, bundle, support_checker=None if a.no_model else model_support_check,
                 fetch_cited=fetch)
    if a.json:
        print(json.dumps(r.to_dict(), indent=2))
    else:
        print(f"{'PASS' if r.passed else 'FAIL'}: {len(r.errors)} errors, {len(r.warnings)} warnings, "
              f"{r.claims_checked} claims, {r.urls_checked} urls")
        for e in r.errors:
            print(f"  ✗ [{e['rule']}] {e['detail']}" + (f"\n      “{e['claim'][:160]}”" if e['claim'] else ""))
    return 0 if r.passed else 1


if __name__ == "__main__":
    sys.exit(main())
