#!/usr/bin/env python3
"""
Content Calendar and Topic Balancing
Tracks topic distribution and ensures diverse content coverage.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import Counter

import yaml

# Configuration
POSTS_DIR = Path("site/content/posts")
CACHE_DIR = Path(".cache")
CACHE_FILE = CACHE_DIR / "topic_distribution.json"
RECENT_ARTICLE_WINDOW = 5  # Check last N articles for similarity

# Tag category mappings for topic analysis
TAG_CATEGORIES = {
    "mowing": ["mow", "cut", "blade", "trimmer", "edger", "height"],
    "fertilizing": ["fertiliz", "npk", "nitrogen", "feed", "nutrient"],
    "watering": ["water", "irrigat", "sprinkler", "drought", "moisture"],
    "weeds": ["weed", "herbicide", "crabgrass", "dandelion", "broadleaf"],
    "aeration": ["aerat", "compact", "core", "plug", "soil"],
    "overseeding": ["seed", "overseed", "germina", "establish"],
    "pest-control": ["pest", "grub", "insect", "fungus", "disease", "fungicide"],
    "equipment": ["mower", "tool", "equipment", "blade", "sharpen", "maintain"],
    "thatch": ["thatch", "dethatch", "scarif"],
    "soil": ["soil", "ph", "test", "amend", "compost"],
}

# Content type patterns
CONTENT_TYPE_PATTERNS = {
    "how-to": [r"how to", r"step.?by.?step", r"guide"],
    "best-time": [r"best time", r"when to", r"when should"],
    "troubleshooting": [r"why is", r"why does", r"problem", r"fix", r"repair"],
    "comparison": [r"vs\.?", r"versus", r"compare", r"difference"],
    "equipment-guide": [r"best \w+ for", r"review", r"buying guide"],
}


def load_all_articles() -> list[dict]:
    """Load all article frontmatter from posts directory."""
    articles = []

    if not POSTS_DIR.exists():
        return []

    for md_file in sorted(POSTS_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            content = md_file.read_text()
            if not content.startswith("---"):
                continue

            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])
            frontmatter["_file_path"] = str(md_file)
            articles.append(frontmatter)

        except Exception as e:
            print(f"   ⚠️  Error loading {md_file.name}: {e}")

    return articles


def categorize_by_tags(article: dict) -> list[str]:
    """
    Categorize article by matching tags/title/keyword against tag categories.

    Returns:
        List of matching category names
    """
    # Combine searchable text
    text_parts = [
        article.get("title", ""),
        article.get("keyword", ""),
        " ".join(article.get("tags", []))
    ]
    text = " ".join(text_parts).lower()

    categories = []
    for category, patterns in TAG_CATEGORIES.items():
        for pattern in patterns:
            if pattern in text:
                categories.append(category)
                break

    return categories if categories else ["other"]


def categorize_content_type(article: dict) -> str:
    """
    Determine content type from title/keyword.

    Returns:
        Content type string
    """
    text = f"{article.get('title', '')} {article.get('keyword', '')}".lower()

    for content_type, patterns in CONTENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return content_type

    return "general"


def analyze_topic_distribution() -> dict:
    """
    Scan all articles and calculate distribution metrics.

    Returns:
        Dict with distribution by season, tags, content type
    """
    articles = load_all_articles()

    if not articles:
        return {"error": "No articles found"}

    # Count by season
    season_counts = Counter(a.get("season", "unknown").lower() for a in articles)

    # Count by tag category
    tag_category_counts = Counter()
    for article in articles:
        for category in categorize_by_tags(article):
            tag_category_counts[category] += 1

    # Count by content type
    content_type_counts = Counter(categorize_content_type(a) for a in articles)

    # Recent articles (last N)
    recent = articles[:RECENT_ARTICLE_WINDOW]
    recent_articles = [
        {
            "slug": a.get("slug"),
            "date": (a.get("generated_at") or "")[:10],
            "season": a.get("season"),
            "tags": a.get("tags", []),
            "categories": categorize_by_tags(a)
        }
        for a in recent
    ]

    distribution = {
        "updated_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "by_season": dict(season_counts),
        "by_tag_category": dict(tag_category_counts),
        "by_content_type": dict(content_type_counts),
        "recent_articles": recent_articles
    }

    # Save to cache
    CACHE_DIR.mkdir(exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(distribution, f, indent=2)

    return distribution


def identify_coverage_gaps() -> list[dict]:
    """
    Find underrepresented topics that need more content.

    Returns:
        List of gap recommendations
    """
    distribution = analyze_topic_distribution()

    if "error" in distribution:
        return []

    gaps = []
    total = distribution["total_articles"]

    # Check season balance (expect roughly equal distribution)
    seasons = ["spring", "summer", "fall", "winter"]
    season_counts = distribution["by_season"]
    avg_per_season = total / 4

    for season in seasons:
        count = season_counts.get(season, 0)
        if count < avg_per_season * 0.6:  # Less than 60% of expected
            gaps.append({
                "type": "season",
                "category": season,
                "current_count": count,
                "expected": round(avg_per_season),
                "priority": "high" if count < avg_per_season * 0.4 else "medium",
                "recommendation": f"Need more {season} content ({count} vs ~{round(avg_per_season)} expected)"
            })

    # Check tag category balance
    tag_counts = distribution["by_tag_category"]
    avg_per_category = total / len(TAG_CATEGORIES)

    for category in TAG_CATEGORIES.keys():
        count = tag_counts.get(category, 0)
        if count < 3:  # Minimum threshold
            gaps.append({
                "type": "tag_category",
                "category": category,
                "current_count": count,
                "priority": "high" if count == 0 else "medium",
                "recommendation": f"Need more {category} content (only {count} articles)"
            })

    return sorted(gaps, key=lambda x: (0 if x["priority"] == "high" else 1, x["current_count"]))


def calculate_keyword_similarity(keyword1: str, keyword2: str) -> float:
    """
    Calculate word overlap similarity between two keywords.

    Returns:
        Similarity score 0.0 to 1.0
    """
    words1 = set(keyword1.lower().replace("-", " ").split())
    words2 = set(keyword2.lower().replace("-", " ").split())

    # Remove common stop words
    stop_words = {"the", "a", "an", "to", "for", "of", "in", "on", "my", "your", "lawn", "grass", "how", "what", "when", "why", "is", "are", "should", "i"}
    words1 = words1 - stop_words
    words2 = words2 - stop_words

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def check_similarity_to_recent(keyword: str, max_recent: int = RECENT_ARTICLE_WINDOW) -> dict:
    """
    Check if new keyword is too similar to recently published articles.

    Returns:
        Dict with similarity analysis
    """
    articles = load_all_articles()[:max_recent]

    highest_similarity = 0.0
    most_similar_slug = None
    most_similar_keyword = None

    for article in articles:
        article_keyword = article.get("keyword", "")
        article_slug = article.get("slug", "")

        # Check keyword similarity
        similarity = calculate_keyword_similarity(keyword, article_keyword)

        # Also check slug similarity
        slug_similarity = calculate_keyword_similarity(keyword, article_slug)

        max_sim = max(similarity, slug_similarity)

        if max_sim > highest_similarity:
            highest_similarity = max_sim
            most_similar_slug = article_slug
            most_similar_keyword = article_keyword

    return {
        "keyword": keyword,
        "highest_similarity": round(highest_similarity, 2),
        "similar_to_slug": most_similar_slug,
        "similar_to_keyword": most_similar_keyword,
        "is_too_similar": highest_similarity > 0.6
    }


def should_publish(keyword: str) -> tuple[bool, str]:
    """
    Check if publishing this keyword maintains good topic balance.

    Returns:
        (should_publish: bool, reason: str)
    """
    # Check similarity to recent articles
    similarity = check_similarity_to_recent(keyword)

    if similarity["is_too_similar"]:
        return False, f"Too similar ({similarity['highest_similarity']:.0%}) to recent article: {similarity['similar_to_slug']}"

    return True, "OK - keyword passes balance checks"


def get_balanced_keyword_recommendations(candidate_keywords: list[dict]) -> list[dict]:
    """
    Re-rank keywords to promote topic diversity.

    Args:
        candidate_keywords: List of keyword dicts with "keyword" and "score" fields

    Returns:
        Re-ranked list with balance adjustments
    """
    gaps = identify_coverage_gaps()
    gap_categories = {g["category"]: g["priority"] for g in gaps}

    distribution = analyze_topic_distribution()
    recent_categories = set()
    for article in distribution.get("recent_articles", []):
        recent_categories.update(article.get("categories", []))

    for candidate in candidate_keywords:
        keyword = candidate.get("keyword", "")
        original_score = candidate.get("score", 0.5)

        # Check what categories this keyword would fill
        temp_article = {"title": keyword, "keyword": keyword, "tags": []}
        keyword_categories = categorize_by_tags(temp_article)

        balance_bonus = 0.0

        # Bonus for filling gaps
        for category in keyword_categories:
            if category in gap_categories:
                balance_bonus += 0.2 if gap_categories[category] == "high" else 0.1

        # Penalty for being in same category as recent articles
        for category in keyword_categories:
            if category in recent_categories:
                balance_bonus -= 0.1

        # Check similarity to recent
        similarity = check_similarity_to_recent(keyword)
        if similarity["is_too_similar"]:
            balance_bonus -= 0.3

        candidate["balance_adjustment"] = round(balance_bonus, 2)
        candidate["adjusted_score"] = round(original_score + balance_bonus, 2)
        candidate["fills_gaps"] = [c for c in keyword_categories if c in gap_categories]

    # Re-sort by adjusted score
    return sorted(candidate_keywords, key=lambda x: x.get("adjusted_score", 0), reverse=True)


def print_distribution_report():
    """Print formatted distribution report to console."""
    distribution = analyze_topic_distribution()

    if "error" in distribution:
        print(f"❌ {distribution['error']}")
        return

    print("\n" + "=" * 60)
    print("📊 CONTENT DISTRIBUTION REPORT")
    print("=" * 60)

    print(f"\n📈 Total Articles: {distribution['total_articles']}")

    print(f"\n🌱 By Season:")
    for season, count in sorted(distribution["by_season"].items(), key=lambda x: x[1], reverse=True):
        pct = count / distribution["total_articles"] * 100
        bar = "█" * int(pct / 5)
        print(f"   {season:12} {count:3} ({pct:4.1f}%) {bar}")

    print(f"\n🏷️  By Topic Category:")
    for category, count in sorted(distribution["by_tag_category"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {category:15} {count:3}")

    print(f"\n📝 By Content Type:")
    for content_type, count in sorted(distribution["by_content_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {content_type:15} {count:3}")

    gaps = identify_coverage_gaps()
    if gaps:
        print(f"\n⚠️  Coverage Gaps ({len(gaps)}):")
        for gap in gaps[:5]:
            priority_icon = "🔴" if gap["priority"] == "high" else "🟡"
            print(f"   {priority_icon} {gap['recommendation']}")

    print(f"\n📅 Recent Articles:")
    for article in distribution["recent_articles"]:
        print(f"   {article['date']} | {article['slug'][:40]}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Content Calendar and Topic Balancing")
    parser.add_argument("--analyze", action="store_true", help="Analyze topic distribution")
    parser.add_argument("--gaps", action="store_true", help="Show coverage gaps")
    parser.add_argument("--check", type=str, help="Check if keyword should be published")

    args = parser.parse_args()

    if args.analyze:
        print_distribution_report()
    elif args.gaps:
        gaps = identify_coverage_gaps()
        if gaps:
            print("\n📊 Coverage Gaps:")
            for gap in gaps:
                print(f"   [{gap['priority'].upper()}] {gap['recommendation']}")
        else:
            print("✅ No significant coverage gaps found")
    elif args.check:
        can_publish, reason = should_publish(args.check)
        if can_publish:
            print(f"✅ {reason}")
        else:
            print(f"⚠️  {reason}")
    else:
        print("Usage:")
        print("  python content_calendar.py --analyze")
        print("  python content_calendar.py --gaps")
        print('  python content_calendar.py --check "spring lawn care tips"')
