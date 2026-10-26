#!/usr/bin/env python3
"""Exceptions-only weekly digest built from .logs/run_reports/*.json.

Reads every .logs/**/run_reports/*.json (including artifacts downloaded from
the Mon/Wed content runs) and summarises the last N days: published, blocked (with top reasons), corrected
after one revision, strain enrichment results and the maintenance fix queue.
Posts to NOTIFICATION_WEBHOOK_URL (Discord/Slack-style JSON) if set, and always
writes .logs/weekly_digest.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "content_fix_queue.json"


def build(days: int = 7) -> str:
    cutoff = datetime.now() - timedelta(days=days)
    pub, blocked, corrected, strains_ok, strains_blocked, rechecks = [], [], [], [], [], []
    seen = set()
    for p in sorted((ROOT / ".logs").rglob("run_reports/*.json")):
        if p.name in seen:
            continue
        seen.add(p.name)
        r = json.loads(p.read_text())
        try:
            ts = datetime.fromisoformat(str(r.get("run_at", "")).replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            ts = datetime.fromtimestamp(p.stat().st_mtime)
        if ts < cutoff:
            continue
        if r.get("kind") == "content" and not r.get("dry_run"):
            pub += r.get("published", [])
            blocked += r.get("blocked", [])
            corrected += r.get("corrected", [])
        elif r.get("kind") == "strain_enrichment":
            strains_ok += r.get("applied", []) + r.get("passed_dry_run", [])
            strains_blocked += r.get("blocked", [])
        elif r.get("kind") == "recheck":
            rechecks.append(r)
    q = json.loads(QUEUE.read_text()) if QUEUE.exists() else {}
    L = [f"**Strain Report weekly fact-gate digest** ({days}d)",
         f"Published: {len(pub)} · Blocked: {len(blocked)} · Auto-corrected: {len(corrected)} · "
         f"Strains enriched: {len(strains_ok)} (blocked {len(strains_blocked)}) · Fix queue: {len(q)}"]
    if blocked:
        L.append("\n**Blocked articles**")
        for b in blocked[:10]:
            L.append(f"- {b.get('keyword')}: {'; '.join(b.get('reasons', [])[:2])[:300]}")
    if strains_blocked:
        L.append("\n**Blocked strains**")
        for b in strains_blocked[:10]:
            L.append(f"- {b['slug']}: {'; '.join(b.get('reasons', [])[:2])[:300]}")
    if rechecks:
        last = rechecks[-1]
        L.append(f"\n**Maintenance re-check**: {last['articles_checked']} checked, "
                 f"{len(last['articles_failed'])} failing; strains: "
                 f"{json.dumps({k: v for k, v in last.get('strains', {}).items() if k != 'broken_source_urls'})}")
    if q:
        L.append("\n**Oldest queued fixes**")
        for k, v in sorted(q.items(), key=lambda kv: kv[1].get("first_seen", ""))[:8]:
            L.append(f"- {k} (since {v.get('first_seen', '?')[:10]}): {(v.get('reasons') or [''])[0][:200]}")
    if pub:
        L.append("\nPublished: " + ", ".join(p.get("slug") or p.get("keyword") for p in pub[:15]))
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--no-send", action="store_true")
    a = ap.parse_args(argv)
    text = build(a.days)
    (ROOT / ".logs").mkdir(exist_ok=True)
    (ROOT / ".logs" / "weekly_digest.md").write_text(text)
    print(text)
    hook = os.getenv("NOTIFICATION_WEBHOOK_URL")
    if hook and not a.no_send:
        try:
            requests.post(hook, json={"content": text[:1900], "text": text[:3900]}, timeout=15)
        except Exception as e:
            print(f"digest webhook failed: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
