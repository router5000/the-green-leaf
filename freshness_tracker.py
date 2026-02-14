#!/usr/bin/env python3
"""
Content Freshness Tracker
Detects stale articles and content needing refresh.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# Configuration
POSTS_DIR = Path("site/content/posts")
REPORTS_DIR = Path("reports")
STALENESS_THRESHOLD_DAYS = 365  # Articles older than this need refresh
SEASONAL_PRE_REFRESH_DAYS = 60  # Refresh seasonal content this many days before season

# Season month mapping (Northern Hemisphere)
SEASON_MONTHS = {
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "fall": [9, 10, 11],
    "winter": [12, 1, 2]
}

# When each season starts (month number)
SEASON_START_MONTH = {
    "spring": 3,
    "summer": 6,
    "fall": 9,
    "winter": 12
}


def parse_article_frontmatter(file_path: Path) -> Optional[dict]:
    """
    Extract frontmatter from markdown file.

    Returns:
        Dict with frontmatter fields or None if parsing fails
    """
    try:
        content = file_path.read_text()
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        frontmatter = yaml.safe_load(parts[1])
        frontmatter["_content"] = parts[2]  # Store content for citation check
        frontmatter["_file_path"] = str(file_path)
        return frontmatter

    except Exception as e:
        print(f"   ⚠️  Error parsing {file_path.name}: {e}")
        return None


def get_article_age_days(article: dict, today: datetime) -> int:
    """Calculate days since article was last updated."""
    last_updated = article.get("last_updated") or article.get("generated_at")
    if not last_updated:
        return 9999  # Unknown age = very old

    try:
        if isinstance(last_updated, str):
            # Handle ISO format timestamps
            updated_date = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        else:
            updated_date = last_updated

        # Make both naive for comparison
        if updated_date.tzinfo:
            updated_date = updated_date.replace(tzinfo=None)

        return (today - updated_date).days

    except Exception:
        return 9999


def identify_outdated_citations(content: str) -> list[str]:
    """
    Find year references in Sources section that may be outdated.

    Returns:
        List of years found that are older than last year
    """
    current_year = datetime.now().year

    # Find the Sources section
    sources_match = re.search(r'## Sources\s*(.+?)(?=\n## |\Z)', content, re.DOTALL | re.IGNORECASE)
    if not sources_match:
        return []

    sources_text = sources_match.group(1)

    # Find year references (2020-2029)
    year_refs = re.findall(r'\b(20[2][0-9])\b', sources_text)

    # Return years older than last year
    return sorted(set(y for y in year_refs if int(y) < current_year - 1))


def days_until_season(season: str, today: datetime) -> int:
    """
    Calculate days until the start of a season.

    Returns:
        Days until season starts (0 if currently in that season, negative if passed this year)
    """
    if season not in SEASON_START_MONTH:
        return 9999

    start_month = SEASON_START_MONTH[season]
    current_year = today.year

    # Calculate season start date for this year and next year
    season_start_this_year = datetime(current_year, start_month, 1)
    season_start_next_year = datetime(current_year + 1, start_month, 1)

    # If season already started this year, use next year
    if today >= season_start_this_year:
        # Check if we're still in the season (season lasts ~3 months)
        season_end_approx = datetime(current_year, (start_month + 2) % 12 + 1, 1) if start_month <= 10 else datetime(current_year + 1, (start_month + 2) % 12 + 1, 1)
        if today < season_end_approx:
            return 0  # Currently in season
        # Season passed, calculate to next year
        return (season_start_next_year - today).days

    return (season_start_this_year - today).days


def check_article_freshness(article: dict, today: datetime) -> dict:
    """
    Evaluate single article for freshness issues.

    Returns:
        Dict with freshness analysis
    """
    slug = article.get("slug", "unknown")
    title = article.get("title", "Unknown Title")
    season = article.get("season", "").lower()
    last_updated = article.get("last_updated") or article.get("generated_at")

    age_days = get_article_age_days(article, today)

    result = {
        "slug": slug,
        "title": title,
        "season": season,
        "last_updated": last_updated,
        "age_days": age_days,
        "issues": []
    }

    # Check 1: General staleness
    if age_days > STALENESS_THRESHOLD_DAYS:
        result["issues"].append({
            "type": "general_staleness",
            "severity": "high" if age_days > 730 else "medium",
            "message": f"Article is {age_days} days old (threshold: {STALENESS_THRESHOLD_DAYS})"
        })

    # Check 2: Seasonal content pre-refresh
    if season and season in SEASON_MONTHS and season != "year-round":
        days_to_season = days_until_season(season, today)
        if 0 < days_to_season <= SEASONAL_PRE_REFRESH_DAYS:
            # Check if it was updated in the current year
            if age_days > 180:  # More than 6 months old
                result["issues"].append({
                    "type": "seasonal_refresh",
                    "severity": "medium",
                    "message": f"Seasonal ({season}) content should be refreshed - {days_to_season} days until season starts"
                })

    # Check 3: Outdated citations
    content = article.get("_content", "")
    if content:
        old_years = identify_outdated_citations(content)
        if old_years:
            result["issues"].append({
                "type": "outdated_citations",
                "severity": "low",
                "message": f"Sources section references outdated years: {', '.join(old_years)}"
            })

    return result


def scan_for_stale_articles() -> dict:
    """
    Scan all articles and generate freshness report.

    Returns:
        Report dict with stale articles, seasonal refresh needs, etc.
    """
    today = datetime.now()

    if not POSTS_DIR.exists():
        return {"error": f"Posts directory not found: {POSTS_DIR}"}

    articles = []
    for md_file in POSTS_DIR.glob("*.md"):
        article = parse_article_frontmatter(md_file)
        if article:
            articles.append(article)

    if not articles:
        return {"error": "No articles found"}

    # Analyze each article
    results = [check_article_freshness(a, today) for a in articles]

    # Categorize issues
    stale_articles = [r for r in results if any(i["type"] == "general_staleness" for i in r["issues"])]
    seasonal_refresh = [r for r in results if any(i["type"] == "seasonal_refresh" for i in r["issues"])]
    citation_warnings = [r for r in results if any(i["type"] == "outdated_citations" for i in r["issues"])]
    healthy_articles = [r for r in results if not r["issues"]]

    report = {
        "generated_at": today.isoformat(),
        "thresholds": {
            "general_staleness_days": STALENESS_THRESHOLD_DAYS,
            "seasonal_pre_refresh_days": SEASONAL_PRE_REFRESH_DAYS
        },
        "summary": {
            "total_articles": len(articles),
            "healthy": len(healthy_articles),
            "stale": len(stale_articles),
            "needs_seasonal_refresh": len(seasonal_refresh),
            "has_citation_warnings": len(citation_warnings)
        },
        "stale_articles": sorted(stale_articles, key=lambda x: x["age_days"], reverse=True),
        "seasonal_refresh_needed": seasonal_refresh,
        "citation_warnings": citation_warnings
    }

    return report


def generate_freshness_report(output_dir: Optional[str] = None) -> Path:
    """
    Generate and save freshness report.

    Returns:
        Path to saved report
    """
    report = scan_for_stale_articles()

    if "error" in report:
        print(f"❌ {report['error']}")
        return None

    # Save report
    output_path = Path(output_dir) if output_dir else REPORTS_DIR
    output_path.mkdir(exist_ok=True)

    report_file = output_path / f"freshness_report_{datetime.now().strftime('%Y%m%d')}.json"

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return report_file


def print_freshness_report():
    """Print formatted freshness report to console."""
    report = scan_for_stale_articles()

    if "error" in report:
        print(f"❌ {report['error']}")
        return

    print("\n" + "=" * 60)
    print("📅 CONTENT FRESHNESS REPORT")
    print("=" * 60)

    s = report["summary"]
    print(f"\n📊 Summary:")
    print(f"   Total articles: {s['total_articles']}")
    print(f"   Healthy: {s['healthy']}")
    print(f"   Stale (>{STALENESS_THRESHOLD_DAYS} days): {s['stale']}")
    print(f"   Needs seasonal refresh: {s['needs_seasonal_refresh']}")
    print(f"   Has citation warnings: {s['has_citation_warnings']}")

    if report["stale_articles"]:
        print(f"\n🚨 Stale Articles ({len(report['stale_articles'])}):")
        for article in report["stale_articles"][:10]:
            severity = "🔴" if article["age_days"] > 730 else "🟡"
            print(f"   {severity} {article['slug']}")
            print(f"      Age: {article['age_days']} days | Last updated: {article['last_updated'][:10] if article['last_updated'] else 'Unknown'}")

    if report["seasonal_refresh_needed"]:
        print(f"\n🌱 Seasonal Refresh Needed ({len(report['seasonal_refresh_needed'])}):")
        for article in report["seasonal_refresh_needed"]:
            print(f"   📆 {article['slug']} ({article['season']})")
            for issue in article["issues"]:
                if issue["type"] == "seasonal_refresh":
                    print(f"      {issue['message']}")

    if report["citation_warnings"]:
        print(f"\n📚 Citation Warnings ({len(report['citation_warnings'])}):")
        for article in report["citation_warnings"][:5]:
            print(f"   ⚠️  {article['slug']}")
            for issue in article["issues"]:
                if issue["type"] == "outdated_citations":
                    print(f"      {issue['message']}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Content Freshness Tracker")
    parser.add_argument("--report", action="store_true", help="Generate freshness report")
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument("--stale-only", action="store_true", help="List only stale articles")

    args = parser.parse_args()

    if args.stale_only:
        report = scan_for_stale_articles()
        if "error" not in report:
            for article in report["stale_articles"]:
                print(f"{article['slug']} ({article['age_days']} days)")
    elif args.report or args.save:
        print_freshness_report()
        if args.save:
            report_path = generate_freshness_report()
            if report_path:
                print(f"📁 Report saved to: {report_path}")
    else:
        print("Usage:")
        print("  python freshness_tracker.py --report")
        print("  python freshness_tracker.py --report --save")
        print("  python freshness_tracker.py --stale-only")
