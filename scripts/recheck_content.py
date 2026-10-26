#!/usr/bin/env python3
"""Weekly maintenance: re-validate published articles (and sourced strains)
with the same blocking fact gate, and queue failures for fixing.

  python scripts/recheck_content.py [--limit N] [--slug SLUG]

Articles: each site/content/posts/*.md is checked with validate_facts using the
pages it cites (fetched fresh) as source text, so link rot, homepage citations,
unsourced THC numbers, medical language and unsupported claims are caught.
Rotates through posts (oldest-checked first) so a run stays within budget.

Strains: rows that have strain_sources get their cited URLs re-checked for 200;
rows without any strain_sources are counted as "unsourced" (backlog for
enrich_strains.py). Read-only against Supabase.

Outputs:
  content_fix_queue.json            persistent queue {slug: {reasons, first_seen, last_seen}}
  .logs/run_reports/recheck_*.json  this run's results (for the weekly digest)
Exit 0 always (findings are data, not a CI failure).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from research import fetch_source  # noqa: E402
from validate_facts import load_article, validate, http_status, model_support_check  # noqa: E402

POSTS = ROOT / "site" / "content" / "posts"
QUEUE = ROOT / "content_fix_queue.json"
CHECKED = ROOT / "data" / "recheck_state.json"
REPORT_DIR = ROOT / ".logs" / "run_reports"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def recheck_articles(limit: int, slugs: list[str] | None) -> list[dict]:
    state = json.loads(CHECKED.read_text()) if CHECKED.exists() else {}
    files = sorted(POSTS.glob("*.md"), key=lambda f: state.get(f.stem, ""))
    if slugs:
        files = [POSTS / f"{s}.md" for s in slugs]
    use_model = bool(os.getenv("ANTHROPIC_API_KEY"))
    out = []
    for f in files[:limit]:
        art = load_article(f)
        res = validate(art, None, url_checker=http_status,
                       support_checker=model_support_check if use_model else None,
                       require_model=use_model,
                       fetch_cited=lambda u: fetch_source(u, "cited").text)
        state[f.stem] = now()
        out.append({"slug": f.stem, "passed": res.passed,
                    "reasons": [f"[{e['rule']}] {e['detail']}" + (f" :: {e['claim'][:140]}" if e['claim'] else "")
                                for e in res.errors][:25]})
        print(f"{'PASS' if res.passed else 'FAIL'} {f.stem} ({len(res.errors)} issues)")
    CHECKED.parent.mkdir(exist_ok=True)
    CHECKED.write_text(json.dumps(state, indent=2))
    return out


def recheck_strains() -> dict:
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    if not url or not key:
        return {"skipped": "no Supabase credentials"}
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    try:
        strains = requests.get(f"{url.rstrip('/')}/rest/v1/strains", headers=h, timeout=30,
                               params={"select": "id,slug,published", "published": "eq.true"}).json()
        r = requests.get(f"{url.rstrip('/')}/rest/v1/strain_sources", headers=h, timeout=30,
                         params={"select": "strain_id,url"})
        if r.status_code != 200:
            return {"skipped": f"strain_sources not readable (HTTP {r.status_code}); migration 004 applied?",
                    "published_strains": len(strains)}
        rows = r.json()
    except Exception as e:
        return {"skipped": f"error: {e}"}
    by = {}
    for s in rows:
        by.setdefault(s["strain_id"], set()).add(s["url"])
    broken = []
    for st in strains:
        for u in sorted(by.get(st["id"], [])):
            code = http_status(u)
            if code != 200:
                broken.append({"slug": st["slug"], "url": u, "status": code})
    return {"published_strains": len(strains),
            "sourced": sum(1 for s in strains if s["id"] in by),
            "unsourced": sum(1 for s in strains if s["id"] not in by),
            "broken_source_urls": broken}


def update_queue(results: list[dict], strains: dict) -> dict:
    q = json.loads(QUEUE.read_text()) if QUEUE.exists() else {}
    t = now()
    for r in results:
        key = f"article:{r['slug']}"
        if r["passed"]:
            q.pop(key, None)
        else:
            e = q.setdefault(key, {"first_seen": t})
            e.update(last_seen=t, reasons=r["reasons"])
    for b in strains.get("broken_source_urls", []) if isinstance(strains, dict) else []:
        e = q.setdefault(f"strain:{b['slug']}", {"first_seen": t})
        e.update(last_seen=t, reasons=[f"source URL returned {b['status']}: {b['url']}"])
    QUEUE.write_text(json.dumps(q, indent=2, sort_keys=True))
    return q


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--slug", action="append")
    ap.add_argument("--no-strains", action="store_true")
    a = ap.parse_args(argv)
    results = recheck_articles(a.limit, a.slug)
    strains = {} if a.no_strains else recheck_strains()
    q = update_queue(results, strains)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rep = {"kind": "recheck", "run_at": now(), "articles_checked": len(results),
           "articles_failed": [r for r in results if not r["passed"]],
           "strains": strains, "queue_size": len(q)}
    p = REPORT_DIR / f"recheck_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    p.write_text(json.dumps(rep, indent=2))
    print(f"🧾 {p}  queue={len(q)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
