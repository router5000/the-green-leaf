#!/usr/bin/env python3
"""
IndexNow submitter for strainreport.com (Bing, Yandex, Seznam, Naver... share submissions).

The key is public by design; it is verified by fetching https://strainreport.com/<key>.txt
(hosted from site/public).

Usage:
  python indexnow.py --urls https://strainreport.com/articles/foo ...
  python indexnow.py --sitemap                 # every URL in sitemap.xml
  python indexnow.py --pending                 # URLs queued by auto_publish (.logs/indexnow_pending.txt)
  add --wait-live 900 to poll each URL until it returns 200 (e.g. right after a deploy)
  add --dry-run to print without submitting
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HOST = "strainreport.com"
KEY = "89c85c116e19bbfbb6fc47d53f9c3265"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
PENDING = Path(__file__).resolve().parent / ".logs" / "indexnow_pending.txt"
UA = {"User-Agent": "StrainReport-IndexNow/1.0"}


def _get(url: str, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def sitemap_urls() -> list[str]:
    status, body = _get(f"https://{HOST}/sitemap.xml")
    if status != 200:
        raise SystemExit(f"sitemap.xml returned {status}")
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)


def queue_pending(urls: list[str]) -> None:
    """Called by auto_publish after a push: remember URLs to submit once deployed."""
    if not urls:
        return
    PENDING.parent.mkdir(parents=True, exist_ok=True)
    existing = set(PENDING.read_text().split()) if PENDING.exists() else set()
    PENDING.write_text("\n".join(sorted(existing | set(urls))) + "\n")


def wait_live(urls: list[str], timeout_s: int) -> list[str]:
    deadline = time.time() + timeout_s
    remaining = list(urls)
    while remaining and time.time() < deadline:
        remaining = [u for u in remaining if _get(u)[0] != 200]
        if remaining:
            time.sleep(30)
    if remaining:
        print(f"⚠️  Not live after {timeout_s}s, skipping: {remaining}")
    return [u for u in urls if u not in remaining]


def submit(urls: list[str], dry_run: bool = False) -> bool:
    urls = [u for u in dict.fromkeys(urls) if u.startswith(f"https://{HOST}/") or u == f"https://{HOST}"]
    if not urls:
        print("Nothing to submit.")
        return True
    ok = True
    for i in range(0, len(urls), 10000):
        batch = urls[i:i + 10000]
        payload = {"host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": batch}
        if dry_run:
            print(f"[dry-run] would submit {len(batch)} URLs")
            continue
        req = urllib.request.Request(
            ENDPOINT, data=json.dumps(payload).encode(), method="POST",
            headers={**UA, "Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"IndexNow: HTTP {r.status} for {len(batch)} URLs")
                ok &= r.status in (200, 202)
        except urllib.error.HTTPError as e:
            print(f"IndexNow: HTTP {e.code} {e.read()[:200]!r}")
            ok = False
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--urls", nargs="*", default=[])
    ap.add_argument("--sitemap", action="store_true")
    ap.add_argument("--pending", action="store_true")
    ap.add_argument("--wait-live", type=int, default=0, metavar="SECONDS")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    urls = list(a.urls)
    if a.sitemap:
        urls += sitemap_urls()
    if a.pending and PENDING.exists():
        urls += PENDING.read_text().split()
    if a.wait_live and urls:
        urls = wait_live(urls, a.wait_live)
    ok = submit(urls, a.dry_run)
    if ok and a.pending and PENDING.exists() and not a.dry_run:
        PENDING.unlink()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
