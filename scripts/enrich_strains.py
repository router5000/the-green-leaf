#!/usr/bin/env python3
"""Fill thin strain pages from verified research (replaces model-memory seeding).

Weekly, in tier order from data/thin_strains_priority.csv, ~5 strains:
  research.py (strain mode)  ->  model drafts fields ONLY from the bundle, with a
  per-sentence source URL  ->  scripts/validate_facts.py gate  ->  projected
  up to 2 targeted revisions of only the failing sentences -> deterministic prune
  of anything still flagged -> all gates re-run -> projected visibleWordCount >= 300
  (else parked as "insufficient sourced material")  ->  (only with --apply) PATCH Supabase strain row +
  insert strain_sources rows.  Failures are logged to the run report and the
  strain is retried next week (max 3 attempts, then parked).

Default is a DRY RUN that writes data/strain_enrichment/<slug>.json only.
--apply needs SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL) + SUPABASE_SECRET_KEY
and the strain_sources table (site/supabase/migrations/004_strain_sources.sql).

Never writes effect_type='medical'. Existing grow fields are left untouched.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from research import research, bundle_for_prompt, ask_model_json, parse_pct, ModelJSONError  # noqa: E402
from validate_facts import validate, CITE_RE, MEDICAL_TERMS, MEDICAL_ALLOW, THC_PCT_RE  # noqa: E402

PRIORITY_CSV = ROOT / "data" / "thin_strains_priority.csv"
STATE_PATH = ROOT / "data" / "strain_enrichment_state.json"
OUT_DIR = ROOT / "data" / "strain_enrichment"
REPORT_DIR = ROOT / ".logs" / "run_reports"
THIN_THRESHOLD = 300          # keep in sync with THIN_STRAIN_WORD_THRESHOLD (strainCatalog.ts)
TARGET_WORDS = 320
MAX_ATTEMPTS = 3
MAX_REVISIONS = 2
PRUNE_RULES = {"medical", "thc", "unsupported"}   # sentence-level gates we can fix by deleting
INSUFFICIENT = "insufficient sourced material"
WRITER_MODEL = "claude-sonnet-4-6"
ALLOWED_EFFECT_TYPES = {"positive", "negative"}


def words(s) -> int:
    """Mirror of words() in site/src/lib/strainCatalog.ts."""
    if not s:
        return 0
    return len([w for w in re.split(r"\s+", str(s).strip()) if w])


def visible_word_count(s: dict) -> int:
    """Mirror of visibleWordCount() in site/src/lib/strainCatalog.ts."""
    n = words(s.get("name")) + words(s.get("short_description")) + words(s.get("description"))
    n += sum(words(a) for a in s.get("aka") or [])
    n += sum(words(e.get("effect_name")) for e in s.get("effects") or [])
    n += sum(words(t.get("terpene_name")) for t in s.get("terpenes") or [])
    n += sum(words(g.get("parent_strain_name")) for g in s.get("genetics") or [])
    n += sum(words(x) for x in (s.get("flavors") or []) + (s.get("aromas") or []) + (s.get("colors") or []))
    for k in ("origin_country", "difficulty", "yield_indoor", "yield_outdoor", "height_indoor", "height_outdoor"):
        n += words(s.get(k))
    return n


# ── Supabase REST (read always allowed; writes only with --apply) ────────────

def sb_conf():
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")
    return (url.rstrip("/"), key) if url and key else (None, None)


def sb_get_strain(slug: str) -> dict | None:
    url, key = sb_conf()
    if not url:
        return None
    r = requests.get(f"{url}/rest/v1/strains", timeout=30,
                     headers={"apikey": key, "Authorization": f"Bearer {key}"},
                     params={"slug": f"eq.{slug}",
                             "select": "*,effects(*),terpenes(*),genetics(*)"})
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def sb_apply(strain: dict, draft: dict, sources: list[dict]) -> None:
    url, key = sb_conf()
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
         "Prefer": "return=minimal"}
    sid = strain["id"]
    patch = {k: draft[k] for k in ("short_description", "description", "aka", "flavors", "aromas", "colors")
             if draft.get(k)}
    if draft.get("origin_country"):
        patch["origin_country"] = draft["origin_country"]
    if draft.get("thc_reported"):
        patch["thc_min"], patch["thc_max"] = draft["thc_reported"]
    requests.patch(f"{url}/rest/v1/strains", params={"id": f"eq.{sid}"}, json=patch, headers=h,
                   timeout=30).raise_for_status()
    # Replace child rows only when the draft provides sourced values.
    for table, rows in (("effects", draft.get("effects")), ("terpenes", draft.get("terpenes")),
                        ("genetics", draft.get("genetics"))):
        if rows:
            requests.delete(f"{url}/rest/v1/{table}", params={"strain_id": f"eq.{sid}"}, headers=h,
                            timeout=30).raise_for_status()
            requests.post(f"{url}/rest/v1/{table}", json=[{"strain_id": sid, **r} for r in rows],
                          headers=h, timeout=30).raise_for_status()
    # Medical effect rows are never kept.
    requests.delete(f"{url}/rest/v1/effects", params={"strain_id": f"eq.{sid}", "effect_type": "eq.medical"},
                    headers=h, timeout=30).raise_for_status()
    if sources:
        requests.post(f"{url}/rest/v1/strain_sources", json=[{"strain_id": sid, **s} for s in sources],
                      headers=h, timeout=30).raise_for_status()


# ── drafting ─────────────────────────────────────────────────────────────────

def structured_facts(bundle: dict) -> dict:
    """Type / lineage / THC / terpene facts as structured fields so the writer
    does not have to (re)interpret them from prose."""
    out = {"type": None, "lineage": [], "thc": [], "terpenes": [], "other": [], "conflicts": []}
    conflicted = {c["field"] for c in bundle.get("conflicts", [])}
    for f in bundle.get("facts", []):
        urls = [e["url"] for e in f.get("evidence", [])]
        item = {"value": f["value"], "sources": urls}
        fld = f["field"]
        if fld in conflicted:
            continue
        if fld == "type" and out["type"] is None:
            out["type"] = item
        elif fld == "lineage":
            out["lineage"].append(item)
        elif fld == "thc_pct":
            out["thc"].append(item)
        elif fld == "terpene":
            out["terpenes"].append(item)
        else:
            out["other"].append({"field": fld, **item})
    out["conflicts"] = [{"field": c["field"], "values": [v["value"] for v in c["values"]]}
                        for c in bundle.get("conflicts", [])]
    return out


WRITER_RULES = """Hard rules (a fact-check gate deletes any sentence that breaks them):
- Use ONLY facts from STRUCTURED FACTS, VERIFIED FACTS or statements that appear verbatim-in-meaning in
  a SOURCE TEXT. If a detail is not there, leave it out. Do not add anything from memory.
- Strain type (indica/sativa/hybrid, "-dominant"), lineage/parents, breeder, origin, awards and
  flavors/aromas: state them ONLY if they appear in STRUCTURED FACTS or a SOURCE TEXT, using the
  exact wording given (e.g. if the type is "hybrid", never write "sativa-dominant hybrid").
  If type is null, do not state a type. Never name a breeder unless a source names it.
- THC: mention a percentage ONLY if it is in STRUCTURED FACTS.thc, phrased as "reported X% THC"
  naming the source (e.g. "Leafly lists a reported 18% THC"), and add that sentence to claims with
  that source's url. Otherwise do not mention any THC number.
- No other numbers (percentages, years, weeks, yields) unless that exact number appears in a SOURCE
  TEXT; such sentences must be in claims with that url.
- Never use medical, condition or treatment language: no treats/relieves/helps with/good for
  pain, anxiety, insomnia, stress, depression, nausea etc., no 'patients', 'therapeutic',
  'medical uses'. Describe reported effects only (e.g. "users report feeling relaxed").
- flavors/aromas/colors/aka arrays: only items a source mentions; give each a field_sources quote.
- If sources disagree (CONFLICTS), say "sources disagree" and do not pick a side."""


def draft_fields(name: str, current: dict, bundle: dict, client=None) -> dict:
    import anthropic
    client = client or anthropic.Anthropic()
    need = max(0, TARGET_WORDS - visible_word_count(current or {"name": name}))
    prompt = f"""Write strain-page fields for "{name}" using ONLY the research material below.
Current page fields (keep only what the sources support; drop anything they do not):
{json.dumps({k: (current or {}).get(k) for k in ('short_description','description','aka','flavors','aromas','colors','origin_country')}, ensure_ascii=False)}

STRUCTURED FACTS (authoritative for type, lineage and THC):
{json.dumps(structured_facts(bundle), ensure_ascii=False, indent=1)}

{WRITER_RULES}
- Every factual sentence in short_description and description must be supported by a SOURCE TEXT.
- The page needs about {need} more visible words; description should be 220-320 words. Reach the
  length with sourced detail (reported effects, aroma, appearance, how sources describe it), never filler claims.
- effects: effect_type is "positive" or "negative" only, effects as reported by sources.

Return ONLY JSON:
{{"short_description": str, "description": str, "aka": [str], "flavors": [str], "aromas": [str],
  "colors": [str], "origin_country": str|null,
  "effects": [{{"effect_name": str, "effect_type": "positive"|"negative", "intensity": 3}}],
  "terpenes": [{{"terpene_name": str}}],
  "genetics": [{{"parent_strain_name": str, "parent_type": "mother"|"father"}}],
  "claims": [{{"sentence": "exact sentence from short_description/description", "url": "exact SOURCE TEXTS url"}}],
  "field_sources": [{{"field": "aka|flavors|aromas|colors|effects|terpenes|genetics|origin_country", "url": str, "quote": "verbatim <=300 chars"}}]}}

RESEARCH MATERIAL:
<<<RESEARCH
{bundle_for_prompt(bundle)}
RESEARCH>>>"""
    return ask_model_json(client, WRITER_MODEL, prompt, expect=dict, max_tokens=5000, timeout=180)


# ── revision / pruning ───────────────────────────────────────────────────────

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    """Same split as as_article(), so gate sentences map back to draft sentences."""
    return [x.strip() for x in SENT_SPLIT.split(text or "") if x.strip()]


def plain_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", CITE_RE.sub("", s or "")).strip()


def failing_sentences(errors: list[dict]) -> dict[str, list[str]]:
    """{plain sentence: [gate messages]} for sentence-level errors we can fix."""
    out: dict[str, list[str]] = {}
    for e in errors:
        if e.get("rule") in PRUNE_RULES and e.get("claim"):
            out.setdefault(plain_sentence(e["claim"]), []).append(f"[{e['rule']}] {e['detail']}")
    return out


def _match(sent: str, failing: dict) -> str | None:
    p = plain_sentence(sent)
    if p in failing:
        return p
    for k in failing:   # gate truncates claims to 300 chars
        if len(k) >= 290 and p.startswith(k[:290]):
            return k
    return None


def is_medical(s: str) -> bool:
    p = plain_sentence(s)
    if any(re.search(a, p, re.I) for a in MEDICAL_ALLOW):
        return False
    return any(re.search(t, p, re.I) for t in MEDICAL_TERMS)


def has_uncited_thc(s: str, claims: dict) -> bool:
    return bool(THC_PCT_RE.search(plain_sentence(s))) and s.strip() not in claims


def _rebuild(draft: dict, keep) -> dict:
    """Rewrite short_description/description keeping sentences where keep(sent) is truthy
    (a string return value replaces the sentence). Claims are kept in sync."""
    new = dict(draft)
    claims = {c["sentence"].strip(): c for c in draft.get("claims") or [] if c.get("sentence")}
    new_claims = []
    for field in ("short_description", "description"):
        out = []
        for sent in split_sentences(draft.get(field, "")):
            k = keep(sent)
            if k is False or k is None or k == "":
                continue
            repl = sent if k is True else str(k).strip()
            out.append(repl)
            if sent in claims:
                c = dict(claims[sent])
                c["sentence"] = repl
                new_claims.append(c)
        new[field] = " ".join(out)
    # claims for replacement sentences supplied by the reviser
    for c in draft.get("_new_claims", []) or []:
        if any(c.get("sentence", "").strip() in split_sentences(new[f]) for f in ("short_description", "description")):
            new_claims.append({"sentence": c["sentence"].strip(), "url": c.get("url")})
    new.pop("_new_claims", None)
    new["claims"] = new_claims
    return new


def prune_flagged(draft: dict, errors: list[dict]) -> tuple[dict, list[dict]]:
    """Deterministically delete every sentence that a gate flagged, plus any sentence
    that still trips the medical regex or carries an uncited THC %. Returns (draft, removed)."""
    failing = failing_sentences(errors)
    claims = {c["sentence"].strip(): c for c in draft.get("claims") or [] if c.get("sentence")}
    removed = []

    def keep(sent):
        why = []
        k = _match(sent, failing)
        if k:
            why += failing[k]
        if is_medical(sent):
            why.append("[medical] regex")
        if has_uncited_thc(sent, claims):
            why.append("[thc] uncited THC %")
        if why:
            removed.append({"sentence": sent, "reasons": sorted(set(why))})
            return False
        return True

    return _rebuild(draft, keep), removed


def apply_revision(draft: dict, errors: list[dict], revision: dict) -> dict:
    """Apply a reviser response {"edits": [{"sentence", "action": "delete"|"rewrite", "new", "url"}]}
    to ONLY the failing sentences; edits aimed at any other sentence are ignored."""
    failing = failing_sentences(errors)
    edits = {}
    new_claims = []
    for e in (revision or {}).get("edits") or []:
        k = _match(e.get("sentence", ""), failing)
        if not k:
            continue
        if e.get("action") == "rewrite" and (e.get("new") or "").strip():
            edits[k] = e["new"].strip()
            if e.get("url"):
                new_claims.append({"sentence": e["new"].strip(), "url": e["url"]})
        else:
            edits[k] = ""

    def keep(sent):
        k = _match(sent, failing)
        if k is None:
            return True
        if k not in edits:      # reviser skipped it: leave it for the deterministic prune
            return True
        return edits[k] or False

    d = dict(draft)
    d["_new_claims"] = new_claims
    return _rebuild(d, keep)


def revise_draft(name: str, draft: dict, errors: list[dict], bundle: dict, client=None) -> dict:
    """Send the reviser only the failing sentences + gate messages; it may delete or
    rewrite those sentences using the provided facts, nothing else."""
    failing = failing_sentences(errors)
    if not failing:
        return draft
    import anthropic
    client = client or anthropic.Anthropic()
    items = "\n".join(f"- SENTENCE: {s}\n  GATE: {'; '.join(m)}" for s, m in failing.items())
    prompt = f"""A fact-check gate rejected these sentences from the "{name}" strain page.
For EACH sentence either delete it or rewrite it so it uses only the facts below. Do not touch any
other sentence and do not add new sentences. If you cannot fix a sentence with the facts, delete it.

{items}

{WRITER_RULES}

STRUCTURED FACTS:
{json.dumps(structured_facts(bundle), ensure_ascii=False, indent=1)}

RESEARCH MATERIAL:
<<<RESEARCH
{bundle_for_prompt(bundle, max_chars_per_source=4000)}
RESEARCH>>>

Return ONLY JSON: {{"edits": [{{"sentence": "exact failing sentence", "action": "delete"|"rewrite",
  "new": "rewritten sentence or empty", "url": "SOURCE TEXTS url supporting the rewrite, or null"}}]}}"""
    rev = ask_model_json(client, WRITER_MODEL, prompt, expect=dict, max_tokens=3000, timeout=120)
    return apply_revision(draft, errors, rev)


def gate(name: str, current: dict, draft: dict, bundle: dict, *, validator=None, reviser=None,
         max_revisions: int = MAX_REVISIONS) -> tuple[dict, list[str], dict]:
    """validate -> up to max_revisions targeted revisions -> deterministic prune of anything
    still flagged -> re-run every gate. Returns (draft, reasons, log). No gate is relaxed:
    the final draft must pass validate() unchanged and the word threshold."""
    validator = validator or (lambda d: validate(as_article(name, d), bundle).errors)
    reviser = reviser or (lambda d, errs: revise_draft(name, d, errs, bundle))
    log = {"revisions": 0, "pruned": []}
    errors = validator(draft)
    while errors and failing_sentences(errors) and log["revisions"] < max_revisions:
        log["revisions"] += 1
        draft = sanitize(reviser(draft, errors))
        errors = validator(draft)
    for _ in range(3):   # pruning only removes text; the model check can surface new flags
        draft, removed = prune_flagged(draft, errors)
        log["pruned"] += removed
        if not removed:
            break
        errors = validator(draft)
    reasons = [f"[{e['rule']}] {e['detail']}" for e in errors]
    pc = projected(current, draft)
    draft["projected_words"] = pc
    if pc < THIN_THRESHOLD:
        reasons.append(f"{INSUFFICIENT}: projected {pc} words < {THIN_THRESHOLD} after removing unsupported sentences")
    return draft, reasons, log


def as_article(name: str, draft: dict) -> dict:
    """Render a strain draft as a cited pseudo-article so validate_facts can
    check it with the same rules as articles."""
    urls = list(dict.fromkeys(c["url"] for c in draft.get("claims", []) if c.get("url")))
    num = {u: i + 1 for i, u in enumerate(urls)}
    claim_url = {c["sentence"].strip(): c["url"] for c in draft.get("claims", []) if c.get("sentence")}
    lines = []
    for field in ("short_description", "description"):
        for sent in re.split(r"(?<=[.!?])\s+", draft.get(field, "") or ""):
            sent = sent.strip()
            if not sent:
                continue
            u = claim_url.get(sent)
            lines.append(sent[:-1] + f"[[{num[u]}]](#user-content-fn-{num[u]})." if u and sent.endswith(".")
                         else sent)
    src = "\n".join(f'<a id="user-content-fn-{n}"></a>\n{n}. [{u}]({u})' for u, n in num.items())
    return {"keyword": f"{name} strain", "title": name, "content": "\n".join(lines) + "\n\n## Sources\n" + src}


def sanitize(draft: dict) -> dict:
    draft["effects"] = [e for e in draft.get("effects") or []
                        if e.get("effect_type") in ALLOWED_EFFECT_TYPES and e.get("effect_name")]
    draft["terpenes"] = [{"terpene_name": t["terpene_name"]} for t in draft.get("terpenes") or []
                         if t.get("terpene_name")]
    return draft


def projected(current: dict, draft: dict) -> int:
    merged = dict(current or {})
    for k in ("short_description", "description", "aka", "flavors", "aromas", "colors", "origin_country",
              "effects", "terpenes", "genetics"):
        if draft.get(k):
            merged[k] = draft[k]
    return visible_word_count(merged)


# ── main ─────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    return json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}


def next_batch(n: int, state: dict) -> list[dict]:
    rows = list(csv.DictReader(PRIORITY_CSV.open()))
    rows = [r for _, r in sorted(enumerate(rows), key=lambda ir: (int(ir[1]["tier"]), ir[0]))]
    out = []
    for r in rows:
        st = state.get(r["slug"], {})
        if st.get("status") in ("applied", "parked"):
            continue
        out.append(r)
        if len(out) >= n:
            break
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--slug", action="append", help="specific slug(s) instead of the queue")
    ap.add_argument("--apply", action="store_true", help="write passing drafts to Supabase")
    a = ap.parse_args(argv)

    if a.apply and not all(sb_conf()):
        print("❌ --apply needs SUPABASE_URL and SUPABASE_SECRET_KEY")
        return 2
    state = load_state()
    batch = [{"slug": s} for s in a.slug] if a.slug else next_batch(a.count, state)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"kind": "strain_enrichment", "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "apply": a.apply, "applied": [], "passed_dry_run": [], "blocked": []}

    for row in batch:
        slug = row["slug"]
        print(f"\n🌿 {slug}")
        st = state.setdefault(slug, {"attempts": 0})
        st["attempts"] += 1
        try:
            current = sb_get_strain(slug) or {"name": slug.replace("-", " ").title(), "slug": slug}
            name = current.get("name") or slug
            if current.get("id") and visible_word_count(current) >= THIN_THRESHOLD:
                st["status"] = "applied"
                print("   already >= threshold; skipping")
                continue
            bundle = json.loads(research(name, kind="strain").to_json())
            (ROOT / "research").mkdir(exist_ok=True)
            (ROOT / "research" / f"strain-{slug}.json").write_text(json.dumps(bundle, indent=2))
            reasons = []
            glog = None
            if len(bundle["sources"]) < 2:
                reasons.append(f"only {len(bundle['sources'])} usable sources")
                draft = {}
            else:
                draft = sanitize(draft_fields(name, current, bundle))
                draft, gate_reasons, glog = gate(name, current, draft, bundle)
                reasons += gate_reasons
                print(f"   revisions: {glog['revisions']}, pruned sentences: {len(glog['pruned'])}")
            (OUT_DIR / f"{slug}.json").write_text(json.dumps(
                {"slug": slug, "draft": draft, "reasons": reasons, "conflicts": bundle.get("conflicts", []),
                 "revision_log": glog},
                indent=2, ensure_ascii=False))
            if reasons:
                insufficient = any(r.startswith(INSUFFICIENT) for r in reasons)
                # Too little sourced material won't change week to week: park now, don't retry.
                st["status"] = "parked" if insufficient or st["attempts"] >= MAX_ATTEMPTS else "blocked"
                if insufficient:
                    st["parked_reason"] = INSUFFICIENT
                    report.setdefault("parked_insufficient", []).append(slug)
                entry = {"slug": slug, "reasons": reasons[:15], "status": st["status"]}
                if draft:
                    entry["revisions"] = glog["revisions"]
                    entry["pruned"] = glog["pruned"][:15]
                report["blocked"].append(entry)
                print(f"   ⛔ blocked: {reasons[:3]}")
                continue
            thc = [f for f in bundle.get("facts", []) if f["field"] == "thc_pct"]
            if thc and not any(c["field"] == "thc_pct" for c in bundle.get("conflicts", [])):
                vals = parse_pct(thc[0]["value"])
                draft["thc_reported"] = (min(vals), max(vals))
                draft.setdefault("field_sources", []).append(
                    {"field": "thc", "url": thc[0]["evidence"][0]["url"], "quote": thc[0]["evidence"][0]["quote"]})
            else:
                report.setdefault("thc_unsourced", []).append(slug)
            fetched = {s["url"]: s["fetched_at"] for s in bundle["sources"]}
            sources = [{"field": "description", "url": c["url"], "quote": c["sentence"][:300],
                        "fetched_at": fetched.get(c["url"])} for c in draft.get("claims", [])]
            sources += [{"field": fs["field"], "url": fs["url"], "quote": fs.get("quote", "")[:300],
                         "fetched_at": fetched.get(fs["url"])} for fs in draft.get("field_sources", [])
                        if fs.get("url") in fetched]
            if a.apply and current.get("id"):
                sb_apply(current, draft, sources)
                st["status"] = "applied"
                report["applied"].append({"slug": slug, "projected_words": draft["projected_words"]})
                print(f"   ✅ applied ({draft['projected_words']} words)")
            else:
                st["status"] = "passed_dry_run"
                report["passed_dry_run"].append({"slug": slug, "projected_words": draft["projected_words"]})
                print(f"   ✅ passed (dry run, {draft['projected_words']} words)")
        except ModelJSONError as e:
            st["status"] = "blocked"
            report["blocked"].append({"slug": slug, "reasons": [f"model JSON: {e}"[:300]]})
            print(f"   ⛔ blocked: {e}")
        except Exception as e:
            st["status"] = "error"
            report["blocked"].append({"slug": slug, "reasons": [f"error: {type(e).__name__}: {e}"[:300]]})
            print(f"   ❌ {e}")
        st["last_run"] = report["run_at"]

    STATE_PATH.write_text(json.dumps(state, indent=2))
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    p = REPORT_DIR / f"strains_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    p.write_text(json.dumps(report, indent=2))
    print(f"\n🧾 {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
