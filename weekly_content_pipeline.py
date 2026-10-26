#!/usr/bin/env python3
"""
Weekly Content Pipeline for The Strain Report Content Engine

Orchestrates the full automated content workflow:
1. Keyword Research - Find best topic to write about
2. Source Research  - research.py fetches sources, keeps facts corroborated by 2+
3. Content Generation - writes ONLY from the research bundle
4. Fact Gate - scripts/validate_facts.py (blocking); auto-revise once, else block
5. Auto-Publish - only items that passed the fact gate (no human gate)
6. Run report - .logs/run_reports/<ts>.json (published / blocked / corrected)

Can be run manually or via GitHub Actions cron job.
"""

import os
import sys
import re
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Import our modules
from keyword_research import find_best_keyword, get_content_pillars
from auto_publish import auto_publish, check_git_status, setup_git_for_ci

load_dotenv()

# Configuration
CONTENT_GENERATOR_PATH = Path("content_generator.py")
LOG_PATH = Path(".logs")

# Publishing is gated ONLY by the automated fact gate (validate_facts.py).
# There is intentionally no per-article human review; exceptions surface in the
# weekly run report / digest. The style QA score is advisory.
PUBLISH_THRESHOLD = 8.0  # advisory style score, kept for logging only
MIN_RESEARCH_SOURCES = 2
RUN_REPORT_DIR = LOG_PATH / "run_reports"


def log_pipeline_run(status: str, keyword: str, details: dict):
    """Log pipeline run for monitoring."""
    LOG_PATH.mkdir(exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "keyword": keyword,
        "details": details
    }
    
    log_file = LOG_PATH / f"pipeline_{datetime.now().strftime('%Y%m')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"📋 Logged to {log_file}")


def run_research(keyword: str) -> tuple[Optional[Path], dict]:
    """Run research.py for a keyword; returns (bundle_path, bundle)."""
    from research import research, save_bundle
    bundle = research(keyword)
    path = save_bundle(bundle)
    data = json.loads(bundle.to_json())
    print(f"   🔬 Research: {len(data['sources'])} sources, {len(data['facts'])} corroborated facts, "
          f"{len(data['conflicts'])} conflicts → {path}")
    return path, data


def _parse_fact_result(stdout: str) -> dict:
    out = {"fact_check": None, "revised": False, "slug": ""}
    for line in stdout.splitlines():
        if line.startswith("PIPELINE_RESULT"):
            m = re.search(r"fact_check=(\w+)", line)
            if m:
                out["fact_check"] = m.group(1)
            out["revised"] = "revised=True" in line
            m = re.search(r"slug=(\S+)", line)
            if m:
                out["slug"] = m.group(1)
    return out


def _fact_errors(slug: str) -> list:
    p = Path("drafts/json") / f"{slug}.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        return (data.get("fact_check") or {}).get("errors", [])
    except Exception:
        return []


def write_run_report(report: dict) -> Path:
    RUN_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = RUN_REPORT_DIR / f"content_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    path.write_text(json.dumps(report, indent=2))
    (LOG_PATH / "run_report_latest.json").write_text(json.dumps(report, indent=2))
    print(f"🧾 Run report: {path}")
    return path


def run_content_generator(
    keyword: str, no_qa: bool = False, force: bool = False, research_path: Optional[Path] = None
) -> tuple[bool, str, Optional[bool], Optional[float]]:
    """
    Run the content generator script with the given keyword.

    Args:
        keyword: Topic to generate.
        no_qa: Skip the QA pipeline.
        force: Skip the duplicate check (used when regenerating a keyword that
            already wrote a draft on the first attempt).

    Returns:
        (success, output, qa_passed, qa_score) where qa_passed/qa_score are
        parsed from the generator's machine-readable PIPELINE_RESULT line
        (None if generation failed or QA was skipped).
    """
    if not CONTENT_GENERATOR_PATH.exists():
        return False, f"Content generator not found at {CONTENT_GENERATOR_PATH}", None, None

    cmd = [sys.executable, str(CONTENT_GENERATOR_PATH), "--keyword", keyword]
    if research_path:
        cmd += ["--research", str(research_path)]
    if no_qa:
        cmd.append("--no-qa")
    if force:
        cmd.append("--force")

    print(f"🔧 Running: {' '.join(cmd)}")

    # Generating one article is a chain of ~9 sequential Claude calls (draft +
    # up to 3 QA evaluate/2 QA refine rounds + YouTube relevance scoring + up
    # to 2 transcript-insight extractions) plus 2 Runware image generations
    # and several YouTube API calls. Each of those now has its own explicit
    # per-request timeout (see CLAUDE_CALL_TIMEOUT in content_generator.py /
    # article_qa.py / youtube_search.py) so a genuinely hung call fails fast
    # instead of stalling silently — this outer timeout just needs to fit the
    # realistic sequential total under normal-but-slow conditions, not guard
    # against a single hang. 5 minutes never fit that; 8 does with headroom.
    GENERATION_TIMEOUT = 480  # 8 minutes
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=GENERATION_TIMEOUT
        )

        if result.returncode != 0:
            return False, result.stderr or result.stdout, None, None

        qa_passed, qa_score = _parse_pipeline_result(result.stdout)
        return True, result.stdout, qa_passed, qa_score

    except subprocess.TimeoutExpired as e:
        # Surface whatever the generator had printed so far (including our
        # new "⏱️" step-timing lines) instead of discarding it — that's the
        # one piece of evidence that shows which step actually stalled.
        partial_output = (e.stdout or b"").decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        tail = partial_output.strip()[-2000:]
        detail = f"Content generation timed out ({GENERATION_TIMEOUT}s limit)"
        if tail:
            detail += f"\nLast output before timeout:\n{tail}"
        return False, detail, None, None
    except Exception as e:
        return False, str(e), None, None


def _parse_pipeline_result(stdout: str) -> tuple[Optional[bool], Optional[float]]:
    """Parse the generator's `PIPELINE_RESULT qa_passed=.. qa_score=..` line."""
    qa_passed, qa_score = None, None
    for line in stdout.splitlines():
        if line.startswith("PIPELINE_RESULT"):
            m = re.search(r"qa_passed=(\w+)", line)
            if m:
                qa_passed = (m.group(1) == "True")
            m = re.search(r"qa_score=([0-9.]+)", line)
            if m:
                qa_score = float(m.group(1))
    return qa_passed, qa_score


def send_notification(
    title: str,
    message: str,
    success: bool = True,
    webhook_url: Optional[str] = None
):
    """
    Send notification about pipeline results.
    Supports Discord/Slack webhooks if configured.
    """
    webhook = webhook_url or os.getenv("NOTIFICATION_WEBHOOK_URL")
    
    if not webhook:
        print(f"📢 {title}: {message}")
        return
    
    import requests
    
    # Discord webhook format
    payload = {
        "embeds": [{
            "title": title,
            "description": message,
            "color": 0x00ff00 if success else 0xff0000,
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    try:
        requests.post(webhook, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Failed to send notification: {e}")


def run_weekly_pipeline(
    keyword: Optional[str] = None,
    count: int = 1,
    no_qa: bool = False,
    no_publish: bool = False,
    dry_run: bool = False,
    force_season: Optional[str] = None,
    is_ci: bool = False
) -> bool:
    """
    Run the complete weekly content pipeline.
    
    Args:
        keyword: Specific keyword to use (skips research if provided)
        count: Number of articles to generate
        no_qa: Skip QA evaluation
        no_publish: Skip auto-publish step
        dry_run: Show what would happen without doing it
        force_season: Override automatic season detection
        is_ci: Running in CI environment (GitHub Actions)
    
    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("🌿 THE STRAIN REPORT WEEKLY CONTENT PIPELINE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Active pillars: {', '.join(get_content_pillars())}")
    print("=" * 60)
    
    if is_ci:
        setup_git_for_ci()
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
    
    generated_articles = []   # passed the fact gate → publish
    failed_keywords = []      # hard errors
    skipped_keywords = []     # blocked by the fact gate / research (reasons logged)
    corrected = []            # passed only after the one automatic revision
    report_items = []

    # Step 1: Keyword Research
    print("\n" + "─" * 40)
    print("STEP 1: KEYWORD RESEARCH")
    print("─" * 40)

    if keyword:
        keywords = [{"keyword": keyword, "season": force_season or "manual", "score": 1.0}]
        print(f"📝 Using provided keyword: {keyword}")
    else:
        keywords = find_best_keyword(count=count, force_season=force_season)
        if not keywords:
            print("❌ No suitable keywords found")
            log_pipeline_run("failed", "none", {"error": "No keywords found"})
            return False

    # Step 2: Research → Generate → Fact gate
    print("\n" + "─" * 40)
    print("STEP 2: RESEARCH → GENERATE → FACT GATE")
    print("─" * 40)

    for i, kw_data in enumerate(keywords, 1):
        kw = kw_data["keyword"]
        print(f"\n📄 Article {i}/{len(keywords)}: \"{kw}\"")

        if dry_run:
            print(f"   Would research, generate and fact-check: {kw}")
            report_items.append({"keyword": kw, "status": "dry_run"})
            continue

        try:
            research_path, bundle = run_research(kw)
        except Exception as e:
            failed_keywords.append(kw)
            report_items.append({"keyword": kw, "status": "error", "reasons": [f"research error: {e}"]})
            continue
        if len(bundle.get("sources", [])) < MIN_RESEARCH_SOURCES:
            reason = f"only {len(bundle.get('sources', []))} usable sources (< {MIN_RESEARCH_SOURCES})"
            skipped_keywords.append({"keyword": kw, "reasons": [reason]})
            report_items.append({"keyword": kw, "status": "blocked", "reasons": [reason],
                                 "research": str(research_path)})
            print(f"   ⏭️  Blocked: {reason}")
            continue

        # One retry only for hard generation errors (timeouts, API errors).
        # A fact-gate failure is NOT retried here: the generator already revised
        # once; a second failure means block and log.
        result = None
        for attempt in range(2):
            success, output, qa_passed, qa_score = run_content_generator(
                kw, no_qa=no_qa, force=(attempt > 0), research_path=research_path)
            if success:
                result = (output, qa_score)
                break
            print(f"   ⚠️ Generation error: {output[:200]}")

        if result is None:
            failed_keywords.append(kw)
            report_items.append({"keyword": kw, "status": "error", "reasons": ["generation failed twice"]})
            continue

        output, qa_score = result
        fr = _parse_fact_result(output)
        item = {"keyword": kw, "slug": fr["slug"], "qa_score_advisory": qa_score,
                "research": str(research_path), "conflicts": bundle.get("conflicts", [])}
        if fr["fact_check"] == "passed":
            generated_articles.append(kw)
            item["status"] = "published" if not no_publish else "passed_not_published"
            if fr["revised"]:
                corrected.append(kw)
                item["corrected"] = True
            print(f"   ✅ Fact gate passed{' after revision' if fr['revised'] else ''}")
        else:
            errs = _fact_errors(fr["slug"])
            reasons = [f"[{e['rule']}] {e['detail']}" + (f" :: {e['claim'][:140]}" if e.get('claim') else "")
                       for e in errs] or ["fact gate failed (no details)"]
            skipped_keywords.append({"keyword": kw, "reasons": reasons})
            item.update(status="blocked", reasons=reasons)
            print(f"   ⛔ Blocked by fact gate ({len(errs)} issues) — draft in drafts/blocked/")
        report_items.append(item)

    # Step 3: Auto-Publish
    print("\n" + "─" * 40)
    print("STEP 3: AUTO-PUBLISH")
    print("─" * 40)
    
    if no_publish:
        print("⏭️  Skipping publish (--no-publish flag)")
    elif not generated_articles:
        print("⏭️  Nothing to publish (no article met the publish threshold this run)")
    else:
        if dry_run:
            status = check_git_status()
            print(f"   Would publish {len(status['new_articles'])} new articles")
        else:
            publish_success = auto_publish(dry_run=dry_run)
            if not publish_success:
                print("⚠️  Auto-publish had issues (check output above)")
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"✅ Published: {len(generated_articles)} articles")
    print(f"⏭️  Blocked by fact gate / research: {len(skipped_keywords)} articles")
    print(f"🛠️  Corrected (passed after one revision): {len(corrected)}")
    print(f"❌ Failed (errors): {len(failed_keywords)} articles")

    if generated_articles:
        print("\nPublished articles:")
        for kw in generated_articles:
            print(f"  • {kw}")

    if skipped_keywords:
        print("\nBlocked keywords:")
        for item in skipped_keywords:
            print(f"  • {item['keyword']} — {item['reasons'][:3]}")

    if failed_keywords:
        print("\nFailed keywords (generation errors):")
        for kw in failed_keywords:
            print(f"  • {kw}")

    # Skips are a normal, non-failing outcome — only hard generation errors fail
    # the run. (A run that publishes nothing because nothing cleared the bar is
    # not an error; there is no human review to fall back to.)
    overall_success = len(failed_keywords) == 0

    write_run_report({
        "kind": "content",
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "published": [r for r in report_items if r.get("status") == "published"],
        "blocked": [r for r in report_items if r.get("status") == "blocked"],
        "corrected": [r for r in report_items if r.get("corrected")],
        "errors": [r for r in report_items if r.get("status") == "error"],
        "items": report_items,
    })

    log_pipeline_run(
        status="success" if overall_success else "failed",
        keyword=keywords[0]["keyword"] if keywords else "none",
        details={
            "published": generated_articles,
            "skipped": skipped_keywords,
            "failed": failed_keywords,
            "dry_run": dry_run
        }
    )

    if not dry_run:
        # Title must make a "nothing published" week obviously different from a
        # normal one — never let an all-skipped run look like business as usual.
        if not overall_success:
            title = "⚠️ Weekly Pipeline: generation errors"
        elif not generated_articles:
            title = f"⚠️ Weekly Pipeline: 0 published, {len(skipped_keywords)} blocked by fact gate"
        else:
            title = "🌿 Weekly Content Pipeline Complete"
        send_notification(
            title=title,
            message=(f"Published {len(generated_articles)}, "
                     f"blocked {len(skipped_keywords)} by fact gate, corrected {len(corrected)}, "
                     f"{len(failed_keywords)} errored"),
            success=overall_success
        )

    return overall_success


def main():
    parser = argparse.ArgumentParser(
        description="Weekly Content Pipeline for Cannabis Site",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-select keyword and generate 1 article
  python weekly_content_pipeline.py
  
  # Generate 3 articles
  python weekly_content_pipeline.py --count 3
  
  # Use specific keyword
  python weekly_content_pipeline.py --keyword "spring cannabis tips"
  
  # Dry run (see what would happen)
  python weekly_content_pipeline.py --dry-run
  
  # Skip QA (faster, cheaper)
  python weekly_content_pipeline.py --no-qa
  
  # Generate but don't publish
  python weekly_content_pipeline.py --no-publish
        """
    )
    
    parser.add_argument(
        "--keyword", "-k",
        type=str,
        help="Specific keyword to write about (skips research)"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=1,
        help="Number of articles to generate (default: 1)"
    )
    parser.add_argument(
        "--season", "-s",
        type=str,
        choices=["spring", "summer", "fall", "winter", "evergreen"],
        help="Force specific season for keyword selection"
    )
    parser.add_argument(
        "--no-qa",
        action="store_true",
        help="Skip QA evaluation (faster, cheaper)"
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Don't auto-publish after generation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without doing it"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Running in CI environment (configures git)"
    )
    
    args = parser.parse_args()
    
    success = run_weekly_pipeline(
        keyword=args.keyword,
        count=args.count,
        no_qa=args.no_qa,
        no_publish=args.no_publish,
        dry_run=args.dry_run,
        force_season=args.season,
        is_ci=args.ci
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
