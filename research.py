#!/usr/bin/env python3
"""Research step: fetch sources and keep only corroborated facts.

Data flow (see content_quality_plan.md):
    keyword / strain name
      -> candidate URLs (Leafly strain page, breeder site via search, cup/award
         records for strains; NORML, state .gov pages, PubMed for guides)
      -> fetched source text  {url, domain, title, text, fetched_at, status}
      -> candidate facts extracted per source, each with a verbatim quote
      -> facts kept only when >= MIN_CORROBORATION independent domains agree
      -> conflicts recorded (same field, different values across sources)
      -> research/<slug>.json  (consumed by content_generator + validate_facts)

Nothing here writes to Supabase or the site; it only produces a JSON bundle.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Optional
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

import requests

RESEARCH_DIR = Path("research")
MIN_CORROBORATION = 2
USER_AGENT = (
    "Mozilla/5.0 (compatible; StrainReportResearchBot/1.0; +https://strainreport.com)"
)
FETCH_TIMEOUT = 20
MAX_TEXT_CHARS = 60_000

# Domains we trust enough to cite. Anything else is fetched only if it is the
# breeder's own site (found via search) and is labelled as such.
TRUSTED_DOMAINS = {
    "leafly.com", "weedmaps.com", "allbud.com", "hightimes.com", "norml.org",
    "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov", "nida.nih.gov", "cdc.gov",
    "fda.gov", "wikipedia.org", "en.wikipedia.org", "projectcbd.org",
    "cannabisbusinesstimes.com", "greenstate.com", "businesswire.com",
    "laweekly.com", "seedfinder.eu", "zalympix.com",
}

AWARD_RE = re.compile(
    r"((?:1st|2nd|3rd|first|second|third|\d+(?:st|nd|rd|th))\s+place[^.]{0,80}?"
    r"(?:cup|crown|award|awards|zalympix|emerald)[^.]{0,40}?(?:19|20)\d\d"
    r"|(?:19|20)\d\d[^.]{0,60}?(?:cannabis cup|cannabis crown|emerald cup|zalympix|sippi cup|copa \w+)"
    r"[^.]{0,60})",
    re.I,
)
THC_RE = re.compile(r"THC[^.%]{0,40}?(\d{1,2}(?:\.\d)?)\s*(?:%|percent)(?:\s*(?:-|–|to)\s*(\d{1,2}(?:\.\d)?)\s*%)?", re.I)
LINEAGE_RE = re.compile(
    r"(?:cross(?:ing)? (?:of|between)|bred from|by crossing|offspring of|child of)\s+"
    r"([A-Z][\w'#.\- ]{1,40}?)\s+(?:and|with|x|×)\s+([A-Z][\w'#.\- ]{1,40}?)(?=[,.;)]|\s+(?:to|and|that|which|\())",
)
LINEAGE_X_RE = re.compile(r"\b([A-Z][\w'#.\-]*(?: [A-Z#\d][\w'#.\-]*){0,3})\s+(?:x|×)\s+([A-Z][\w'#.\-]*(?: [A-Z#\d][\w'#.\-]*){0,3})\b")
LINEAGE_STOPWORDS = {"enter", "search", "filter", "filters", "allbud", "leafly", "weedmaps", "menu",
                     "login", "sign", "shop", "deals", "reviews", "the", "and", "with"}
TERPENES = ["myrcene", "limonene", "caryophyllene", "pinene", "terpinolene",
            "linalool", "ocimene", "humulene", "bisabolol"]


@dataclass
class Source:
    url: str
    domain: str
    kind: str  # strain_db | breeder | award | law | study | guide | search
    title: str = ""
    text: str = ""
    fetched_at: str = ""
    status: int = 0
    error: str = ""


@dataclass
class Fact:
    field: str           # thc_pct | award | lineage | terpene | type | other
    value: str           # normalized value used for corroboration
    quote: str           # verbatim snippet from the source text
    url: str
    domain: str


@dataclass
class ResearchBundle:
    subject: str
    slug: str
    kind: str            # strain | guide | law
    generated_at: str
    sources: list = field(default_factory=list)
    facts: list = field(default_factory=list)          # corroborated only
    single_source_facts: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


# ── helpers ──────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(s: str) -> str:
    s = re.sub(r"[''`]", "", s.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def base_domain(url: str) -> str:
    host = urlparse(url).netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if host.endswith(".gov") or host.endswith(".nih.gov"):
        return host
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def html_to_text(raw: str) -> tuple[str, str]:
    title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    title = html.unescape(title_m.group(1).strip()) if title_m else ""
    raw = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>|</div>", "\n", raw, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return title, text.strip()[:MAX_TEXT_CHARS]


Fetcher = Callable[[str], tuple[int, str]]


def http_fetch(url: str) -> tuple[int, str]:
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=FETCH_TIMEOUT,
                     allow_redirects=True)
    return r.status_code, r.text


def fetch_source(url: str, kind: str, fetcher: Fetcher = http_fetch) -> Source:
    src = Source(url=url, domain=base_domain(url), kind=kind, fetched_at=now_iso())
    try:
        status, body = fetcher(url)
        src.status = status
        if status == 200:
            src.title, src.text = html_to_text(body)
        else:
            src.error = f"HTTP {status}"
    except Exception as e:  # network errors are recorded, never fatal
        src.error = f"{type(e).__name__}: {e}"[:300]
    return src


def web_search(query: str, limit: int = 5, fetcher: Fetcher = http_fetch) -> list[str]:
    """Return result URLs for a query. Order of backends:
      1. Anthropic server-side web_search tool (uses the existing ANTHROPIC_API_KEY;
         web search must be enabled for the org in the Anthropic console)
      2. Brave Search API if BRAVE_SEARCH_API_KEY is set
      3. DuckDuckGo HTML (often bot-challenged; best-effort)
    Always returns a list (possibly empty); never raises."""
    for backend in (_search_anthropic, _search_brave, _search_ddg):
        try:
            urls = backend(query, limit, fetcher)
        except Exception as e:
            print(f"   research: {backend.__name__} failed: {type(e).__name__}: {str(e)[:120]}")
            urls = []
        if urls:
            return urls[:limit]
    return []


SEARCH_MODEL = os.getenv("RESEARCH_SEARCH_MODEL", "claude-haiku-4-5-20251001")


def _search_anthropic(query: str, limit: int, fetcher: Fetcher) -> list[str]:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return []
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=SEARCH_MODEL, max_tokens=512, timeout=60,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 1}],
        messages=[{"role": "user", "content": f"Search the web for: {query}. Reply with the word done."}],
    )
    urls = []
    for block in msg.content:
        if getattr(block, "type", "") == "web_search_tool_result":
            for item in getattr(block, "content", []) or []:
                u = getattr(item, "url", None)
                if u and u not in urls:
                    urls.append(u)
    return urls[:limit]


def _search_brave(query: str, limit: int, fetcher: Fetcher) -> list[str]:
    key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not key:
        return []
    r = requests.get("https://api.search.brave.com/res/v1/web/search",
                     params={"q": query, "count": limit},
                     headers={"X-Subscription-Token": key, "Accept": "application/json"},
                     timeout=FETCH_TIMEOUT)
    r.raise_for_status()
    return [x["url"] for x in r.json().get("web", {}).get("results", [])][:limit]


def _search_ddg(query: str, limit: int, fetcher: Fetcher) -> list[str]:
    status, body = fetcher(f"https://html.duckduckgo.com/html/?q={quote_plus(query)}")
    if status != 200:
        return []
    urls = []
    for href in re.findall(r'class="result__a"[^>]*href="([^"]+)"', body):
        if "uddg=" in href:
            href = unquote(parse_qs(urlparse(href).query).get("uddg", [href])[0])
        if href.startswith("http") and href not in urls:
            urls.append(href)
    return urls[:limit]


def pubmed_search(query: str, limit: int = 3, fetcher: Fetcher = http_fetch) -> list[str]:
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json"
           f"&retmax={limit}&term={quote_plus(query)}")
    try:
        status, body = fetcher(url)
        ids = json.loads(body)["esearchresult"]["idlist"] if status == 200 else []
    except Exception:
        ids = []
    return [f"https://pubmed.ncbi.nlm.nih.gov/{i}/" for i in ids]


# ── candidate source lists ───────────────────────────────────────────────────

def strain_candidate_urls(name: str, search: Callable[[str], list[str]] = web_search) -> list[tuple[str, str]]:
    slug = slugify(name)
    urls = [
        (f"https://www.leafly.com/strains/{slug}", "strain_db"),
        (f"https://weedmaps.com/strains/{slug}", "strain_db"),
    ] + [(f"https://www.allbud.com/marijuana-strains/{t}/{slug}", "strain_db")
         for t in ("indica-dominant-hybrid", "sativa-dominant-hybrid", "hybrid", "indica", "sativa")]
    for u in search(f'"{name}" strain breeder genetics')[:3]:
        urls.append((u, "breeder"))
    for u in search(f'"{name}" cannabis cup OR emerald cup OR zalympix winner')[:3]:
        urls.append((u, "award"))
    return _dedupe(urls)


def guide_candidate_urls(keyword: str, search: Callable[[str], list[str]] = web_search,
                         pubmed: Callable[[str], list[str]] = pubmed_search) -> list[tuple[str, str]]:
    urls = []
    for u in search(f"site:norml.org {keyword}")[:2]:
        urls.append((u, "guide"))
    if is_law_topic(keyword):
        for u in search(f"site:.gov {keyword} cannabis law")[:3]:
            urls.append((u, "law"))
    for u in pubmed(f"cannabis {keyword}")[:3]:
        urls.append((u, "study"))
    for u in search(f"{keyword} cannabis")[:3]:
        urls.append((u, "guide"))
    return _dedupe(urls)


def is_law_topic(keyword: str) -> bool:
    return bool(re.search(r"\b(legal|law|laws|legaliz|possession|dispensar(y|ies) in|state|travel|fly|flying|tsa|penalt)", keyword, re.I))


def _dedupe(pairs: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    seen, out = set(), []
    for u, k in pairs:
        if u not in seen:
            seen.add(u)
            out.append((u, k))
    return out


# ── fact extraction (deterministic; every fact carries a verbatim quote) ─────

def _sentence_around(text: str, start: int, end: int, pad: int = 160) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    seg = text[a:b]
    return re.sub(r"\s+", " ", seg).strip()


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9#]+", " ", s.lower()).strip()


def extract_facts(src: Source, subject: str) -> list[Fact]:
    """Pull candidate facts from one source. Only text that mentions the
    subject (or comes from a page about it) is used."""
    text = src.text
    if not text:
        return []
    subj = subject.lower()
    if subj not in text.lower() and src.kind not in ("law", "study", "guide"):
        return []
    facts: list[Fact] = []
    low = text.lower()

    for m in THC_RE.finditer(text):
        if src.kind in ("strain_db", "breeder", "award") and subj not in low[max(0, m.start() - 200): m.end() + 40]:
            continue
        lo = m.group(1)
        hi = m.group(2)
        val = f"{float(lo):g}" if not hi else f"{float(lo):g}-{float(hi):g}"
        facts.append(Fact("thc_pct", val, _sentence_around(text, m.start(), m.end()), src.url, src.domain))

    for m in AWARD_RE.finditer(text):
        snippet = m.group(0)
        year = re.search(r"(19|20)\d\d", snippet)
        event = re.search(r"cannabis cup|cannabis crown|emerald cup|zalympix|sippi cup|copa \w+", snippet, re.I)
        if year and event:
            val = f"{year.group(0)} {event.group(0).lower()}"
            facts.append(Fact("award", val, _sentence_around(text, m.start(), m.end(), 60), src.url, src.domain))

    for rx in (LINEAGE_RE, LINEAGE_X_RE):
        for m in rx.finditer(text):
            a, b = norm_name(m.group(1)), norm_name(m.group(2))
            if not a or not b or a == b or subj in (a, b):
                continue
            if any(w in LINEAGE_STOPWORDS for w in (a + " " + b).split()):
                continue
            # Only keep crosses mentioned near the subject name.
            window = text[max(0, m.start() - 250): m.end() + 250].lower()
            if subj not in window:
                continue
            val = " x ".join(sorted([a, b]))
            facts.append(Fact("lineage", val, _sentence_around(text, m.start(), m.end(), 80), src.url, src.domain))

    low = text.lower()
    for t in TERPENES:
        i = low.find(t)
        if i >= 0 and subj in low[max(0, i - 400): i + 400]:
            facts.append(Fact("terpene", t, _sentence_around(text, i, i + len(t), 100), src.url, src.domain))

    for typ in ("indica", "sativa", "hybrid"):
        m = re.search(rf"\b{typ}(?:-dominant)?\b", text, re.I)
        if m and subj in low[max(0, m.start() - 80): m.end() + 80]:
            facts.append(Fact("type", typ, _sentence_around(text, m.start(), m.end(), 80), src.url, src.domain))
    return facts


EXTRACT_MODEL = os.getenv("RESEARCH_EXTRACT_MODEL", "claude-haiku-4-5-20251001")
LLM_FIELDS = ("award", "lineage", "breeder", "origin", "thc_pct", "terpene", "type",
              "flavor", "effect", "law", "study_finding", "other")


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def llm_extract_facts(src: Source, subject: str, client=None) -> list[Fact]:
    """Optional model-assisted extraction. The model must return a verbatim
    quote for every fact; any fact whose quote is not literally present in the
    fetched text is discarded, so the model cannot add facts of its own."""
    if client is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            return []
        import anthropic
        client = anthropic.Anthropic()
    prompt = (
        f"Extract factual claims about \"{subject}\" from the page text below.\n"
        f"Return ONLY a JSON array of objects {{field, value, quote}}. field is one of {list(LLM_FIELDS)}.\n"
        "value is a short canonical lowercase form (e.g. '2010 colorado cannabis crown 1st place', "
        "'og kush x trainwreck', '18'). quote MUST be copied verbatim from the text (max 300 chars).\n"
        "Do not use outside knowledge. Skip anything about other strains or products.\n\n"
        f"URL: {src.url}\nTEXT:\n{src.text[:20000]}"
    )
    try:
        msg = client.messages.create(model=EXTRACT_MODEL, max_tokens=2000, timeout=90,
                                     messages=[{"role": "user", "content": prompt}])
        raw = msg.content[0].text
        raw = raw[raw.find("["): raw.rfind("]") + 1]
        items = json.loads(raw) if raw else []
    except Exception as e:
        print(f"   research: llm extraction failed for {src.url}: {type(e).__name__}")
        return []
    hay = _ws(src.text)
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        q, fld, val = str(it.get("quote", "")), str(it.get("field", "")), str(it.get("value", ""))
        if fld in LLM_FIELDS and q and val and _ws(q) in hay:
            out.append(Fact(fld, _ws(val), q.strip(), src.url, src.domain))
    return out


def _thc_overlaps(a: str, b: str, tol: float = 1.0) -> bool:
    def rng(v):
        p = [float(x) for x in v.split("-")]
        return (p[0], p[-1])
    (a1, a2), (b1, b2) = rng(a), rng(b)
    return a1 - tol <= b2 and b1 - tol <= a2


def corroborate(facts: list[Fact], min_sources: int = MIN_CORROBORATION) -> tuple[list[dict], list[dict], list[dict]]:
    """Group facts by (field, value) and keep those seen on >= min_sources
    distinct domains. Returns (corroborated, single_source, conflicts)."""
    groups: dict[tuple[str, str], list[Fact]] = {}
    for f in facts:
        groups.setdefault((f.field, f.value), []).append(f)

    # THC: merge overlapping numeric values so 19 and 18-21 corroborate.
    thc_keys = [k for k in groups if k[0] == "thc_pct"]
    for i, k1 in enumerate(thc_keys):
        for k2 in thc_keys[i + 1:]:
            if _thc_overlaps(k1[1], k2[1]):
                groups[k1] = groups[k1] + [f for f in groups[k2] if f not in groups[k1]]

    corroborated, single = [], []
    for (fld, val), items in groups.items():
        domains = sorted({f.domain for f in items})
        rec = {
            "field": fld, "value": val, "domains": domains,
            "evidence": [{"url": f.url, "quote": f.quote} for f in _one_per_domain(items)],
        }
        (corroborated if len(domains) >= min_sources else single).append(rec)

    conflicts = []
    for fld in ("thc_pct", "type", "lineage"):
        vals = [c for c in corroborated + single if c["field"] == fld]
        if fld == "thc_pct":
            vals = [v for v in vals if not any(
                _thc_overlaps(v["value"], w["value"]) for w in vals if w is not v)] if len(vals) > 1 else []
        if len({v["value"] for v in vals}) > 1:
            conflicts.append({"field": fld, "values": [
                {"value": v["value"], "domains": v["domains"]} for v in vals]})
    return corroborated, single, conflicts


def _one_per_domain(items: list[Fact]) -> list[Fact]:
    seen, out = set(), []
    for f in items:
        if f.domain not in seen:
            seen.add(f.domain)
            out.append(f)
    return out


# ── entry points ─────────────────────────────────────────────────────────────

def research(subject: str, kind: str = "auto", fetcher: Fetcher = http_fetch,
             search: Optional[Callable[[str], list[str]]] = None,
             pubmed: Optional[Callable[[str], list[str]]] = None,
             polite_delay: float = 0.5, use_llm: bool = True) -> ResearchBundle:
    search = search or (lambda q: web_search(q, fetcher=fetcher))
    pubmed = pubmed or (lambda q: pubmed_search(q, fetcher=fetcher))
    if kind == "auto":
        kind = "law" if is_law_topic(subject) else ("strain" if re.search(r"\bstrain\b", subject, re.I) else "guide")
    strain_name = re.sub(r"\b(strain|profile|review|guide|effects|lineage)\b", "", subject, flags=re.I).strip()

    if kind == "strain":
        candidates = strain_candidate_urls(strain_name, search)
        subj = strain_name
    else:
        candidates = guide_candidate_urls(subject, search, pubmed)
        subj = subject

    sources: list[Source] = []
    got_allbud = False
    for url, k in candidates:
        if "allbud.com" in url and got_allbud:
            continue
        s = fetch_source(url, k, fetcher)
        # Soft-404s: a strain DB page must be about this strain.
        if k == "strain_db" and s.status == 200 and subj.lower() not in s.title.lower():
            s.status, s.error = 0, "title does not mention subject (soft 404)"
        if "allbud.com" in url and s.status == 200:
            got_allbud = True
        sources.append(s)
        time.sleep(polite_delay)

    all_facts: list[Fact] = []
    for s in sources:
        if s.status == 200:
            all_facts.extend(extract_facts(s, subj))
            if use_llm:
                all_facts.extend(llm_extract_facts(s, subj))
    corroborated, single, conflicts = corroborate(all_facts)
    return ResearchBundle(
        subject=subj, slug=slugify(subject), kind=kind, generated_at=now_iso(),
        sources=[asdict(s) for s in sources if s.status == 200 and s.text],
        facts=corroborated, single_source_facts=single, conflicts=conflicts,
    )


def save_bundle(bundle: ResearchBundle, out_dir: Path = RESEARCH_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{bundle.slug}.json"
    p.write_text(bundle.to_json())
    return p


def load_bundle(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def bundle_for_prompt(bundle: dict, max_chars_per_source: int = 6000) -> str:
    """Render a bundle as the ONLY material the generator may use."""
    lines = ["VERIFIED FACTS (corroborated by 2+ independent sources):"]
    for f in bundle.get("facts", []):
        urls = ", ".join(e["url"] for e in f["evidence"])
        lines.append(f"- [{f['field']}] {f['value']}  (sources: {urls})")
    if bundle.get("conflicts"):
        lines.append("\nCONFLICTS (mention only as 'sources disagree', never pick a side):")
        for c in bundle["conflicts"]:
            lines.append(f"- {c['field']}: " + "; ".join(
                f"{v['value']} ({', '.join(v['domains'])})" for v in c["values"]))
    lines.append("\nSOURCE TEXTS (cite these exact URLs; nothing else):")
    for i, s in enumerate(bundle.get("sources", []), 1):
        lines.append(f"\n[S{i}] {s['url']}  (fetched {s['fetched_at']}, kind={s['kind']})\n"
                     f"{s['text'][:max_chars_per_source]}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fetch and corroborate sources for a keyword or strain")
    ap.add_argument("subject")
    ap.add_argument("--kind", default="auto", choices=["auto", "strain", "guide", "law"])
    ap.add_argument("--out", default=str(RESEARCH_DIR))
    a = ap.parse_args(argv)
    b = research(a.subject, a.kind)
    p = save_bundle(b, Path(a.out))
    print(f"research: {len(b.sources)} sources, {len(b.facts)} corroborated facts, "
          f"{len(b.conflicts)} conflicts -> {p}")
    return 0 if b.sources else 2


if __name__ == "__main__":
    sys.exit(main())
