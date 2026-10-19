"""
Refresh strain_index.json (name/slug map used by internal_linker strain links).

The content pipeline has no DB credentials in CI, so the index is a committed
cache. Refresh it locally (or anywhere Supabase read access exists) with:

    NEXT_PUBLIC_SUPABASE_URL=... NEXT_PUBLIC_SUPABASE_ANON_KEY=... python refresh_strain_index.py

Falls back to scraping https://strainreport.com/sitemap.xml + /strains/a-z when
no Supabase env is set (names then come from the A–Z page link text).
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).parent / "strain_index.json"


def from_supabase(url: str, key: str):
    req = urllib.request.Request(
        f"{url}/rest/v1/strains?select=name,slug,strain_type&published=eq.true&order=name",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def from_site():
    html = urllib.request.urlopen("https://strainreport.com/strains/a-z", timeout=30).read().decode()
    rows = re.findall(r'href="/strains/([a-z0-9-]+)"[^>]*>([^<]+)</a>', html)
    skip = {"indica", "sativa", "hybrid", "compare", "a-z"}
    seen, out = set(), []
    for slug, name in rows:
        if slug in skip or slug in seen:
            continue
        seen.add(slug)
        out.append({"name": name.strip(), "slug": slug})
    return out


def main():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    strains = from_supabase(url, key) if url and key else from_site()
    if not strains:
        sys.exit("no strains fetched; leaving strain_index.json unchanged")
    data = {"source": "supabase" if url and key else "site", "strains": [{"name": s["name"], "slug": s["slug"]} for s in strains]}
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(strains)} strains to {OUT.name}")


if __name__ == "__main__":
    main()
