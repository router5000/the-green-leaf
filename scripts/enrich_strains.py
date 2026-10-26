#!/usr/bin/env python3
"""Fill thin strain pages from verified research (replaces model-memory seeding).

Weekly, in tier order from data/thin_strains_priority.csv, ~5 strains:
  research.py (strain mode)  ->  model drafts fields ONLY from the bundle, with a
  per-sentence source URL  ->  scripts/validate_facts.py gate  ->  projected
  visibleWordCount >= 300  ->  (only with --apply) PATCH Supabase strain row +
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
from validate_facts import validate  # noqa: E402

PRIORITY_CSV = ROOT / "data" / "thin_strains_priority.csv"
STATE_PATH = ROOT / "data" / "strain_enrichment_state.json"
OUT_DIR = ROOT / "data" / "strain_enrichment"
REPORT_DIR = ROOT / ".logs" / "run_reports"
THIN_THRESHOLD = 300          # keep in sync with THIN_STRAIN_WORD_THRESHOLD (strainCatalog.ts)
TARGET_WORDS = 320
MAX_ATTEMPTS = 3
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

def draft_fields(name: str, current: dict, bundle: dict, client=None) -> dict:
    import anthropic
    client = client or anthropic.Anthropic()
    need = max(0, TARGET_WORDS - visible_word_count(current or {"name": name}))
    prompt = f"""Write strain-page fields for "{name}" using ONLY the research material below.
Current page fields (keep what is accurate, fix what the sources contradict):
{json.dumps({k: (current or {}).get(k) for k in ('short_description','description','aka','flavors','aromas','colors','origin_country')}, ensure_ascii=False)}

Rules:
- Every factual sentence in short_description and description must be supported by a SOURCE TEXT.
- THC only as "reported X%" naming the source (e.g. "Leafly lists a reported 18% THC"). Never a range you made up.
- Awards and lineage only if they appear in VERIFIED FACTS or the source texts; if sources disagree, say so.
- No medical claims (no treats/relieves/helps with conditions, no 'patients').
- The page needs about {need} more visible words; description should be 220-320 words.
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
            if len(bundle["sources"]) < 2:
                reasons.append(f"only {len(bundle['sources'])} usable sources")
                draft = {}
            else:
                draft = sanitize(draft_fields(name, current, bundle))
                res = validate(as_article(name, draft), bundle)
                reasons += [f"[{e['rule']}] {e['detail']}" for e in res.errors]
                pc = projected(current, draft)
                draft["projected_words"] = pc
                if pc < THIN_THRESHOLD:
                    reasons.append(f"projected {pc} words < {THIN_THRESHOLD}")
            (OUT_DIR / f"{slug}.json").write_text(json.dumps(
                {"slug": slug, "draft": draft, "reasons": reasons, "conflicts": bundle.get("conflicts", [])},
                indent=2, ensure_ascii=False))
            if reasons:
                st["status"] = "parked" if st["attempts"] >= MAX_ATTEMPTS else "blocked"
                report["blocked"].append({"slug": slug, "reasons": reasons[:15]})
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
