#!/usr/bin/env python3
"""
Weekly Content Pipeline for The Green Leaf Content Engine

Orchestrates the full automated content workflow:
1. Keyword Research - Find best topic to write about
2. Content Generation - Create article with images, videos, QA
3. Auto-Publish - Commit and push to trigger deployment

Can be run manually or via GitHub Actions cron job.
"""

import os
import sys
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
MAX_RETRIES = 2


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


def run_content_generator(keyword: str, no_qa: bool = False) -> tuple[bool, str]:
    """
    Run the content generator script with the given keyword.
    
    Returns:
        Tuple of (success, output/error message)
    """
    if not CONTENT_GENERATOR_PATH.exists():
        return False, f"Content generator not found at {CONTENT_GENERATOR_PATH}"
    
    cmd = [sys.executable, str(CONTENT_GENERATOR_PATH), "--keyword", keyword]
    if no_qa:
        cmd.append("--no-qa")
    
    print(f"🔧 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr or result.stdout
            
    except subprocess.TimeoutExpired:
        return False, "Content generation timed out (5 min limit)"
    except Exception as e:
        return False, str(e)


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
    print("🌿 CANNABIS CARE WEEKLY CONTENT PIPELINE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Active pillars: {', '.join(get_content_pillars())}")
    print("=" * 60)
    
    if is_ci:
        setup_git_for_ci()
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
    
    generated_articles = []
    failed_keywords = []
    
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
    
    # Step 2: Content Generation
    print("\n" + "─" * 40)
    print("STEP 2: CONTENT GENERATION")
    print("─" * 40)
    
    for i, kw_data in enumerate(keywords, 1):
        kw = kw_data["keyword"]
        print(f"\n📄 Article {i}/{len(keywords)}: \"{kw}\"")
        
        if dry_run:
            print(f"   Would generate article for: {kw}")
            generated_articles.append(kw)
            continue
        
        # Try generation with retries
        success = False
        for attempt in range(MAX_RETRIES + 1):
            if attempt > 0:
                print(f"   Retry {attempt}/{MAX_RETRIES}...")
            
            success, output = run_content_generator(kw, no_qa=no_qa)
            
            if success:
                print(f"   ✅ Successfully generated article")
                generated_articles.append(kw)
                break
            else:
                print(f"   ⚠️ Generation failed: {output[:200]}")
        
        if not success:
            failed_keywords.append(kw)
            print(f"   ❌ Failed after {MAX_RETRIES + 1} attempts")
    
    # Step 3: Auto-Publish
    print("\n" + "─" * 40)
    print("STEP 3: AUTO-PUBLISH")
    print("─" * 40)
    
    if no_publish:
        print("⏭️  Skipping publish (--no-publish flag)")
    elif not generated_articles:
        print("⏭️  Nothing to publish (no articles generated)")
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
    print(f"✅ Generated: {len(generated_articles)} articles")
    print(f"❌ Failed: {len(failed_keywords)} articles")
    
    if generated_articles:
        print("\nGenerated articles:")
        for kw in generated_articles:
            print(f"  • {kw}")
    
    if failed_keywords:
        print("\nFailed keywords:")
        for kw in failed_keywords:
            print(f"  • {kw}")
    
    # Log and notify
    overall_success = len(generated_articles) > 0
    
    log_pipeline_run(
        status="success" if overall_success else "failed",
        keyword=keywords[0]["keyword"] if keywords else "none",
        details={
            "generated": generated_articles,
            "failed": failed_keywords,
            "dry_run": dry_run
        }
    )
    
    if not dry_run:
        send_notification(
            title="🌿 Weekly Content Pipeline Complete" if overall_success else "⚠️ Pipeline Issues",
            message=f"Generated {len(generated_articles)} articles, {len(failed_keywords)} failed",
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
