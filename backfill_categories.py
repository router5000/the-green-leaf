#!/usr/bin/env python3
"""
Backfill category field into article frontmatter.
Uses the same topic cluster matching logic as the topics page.
"""

import re
from pathlib import Path

import yaml

POSTS_DIR = Path("site/content/posts")

# Topic clusters - title/keyword patterns are the primary signal
# since many articles have only generic tags
CLUSTERS = [
    {
        "id": "weed-control",
        "category": "Weed Control",
        "title_keywords": ["weed", "crabgrass", "spurge", "pre-emergent", "post-emergent", "herbicide", "kill"],
        "tags": ["weed control", "pre-emergent", "post-emergent", "crabgrass"],
    },
    {
        "id": "cannabis-problems",
        "category": "Cannabis Problems & Solutions",
        "title_keywords": ["problem", "disease", "fungus", "fungicide", "yellow", "dead spot", "brown spot", "bumpy", "patchy", "bare spot", "not growing"],
        "tags": ["cannabis problems", "disease prevention", "fungicide", "cannabis diseases", "dead grass"],
    },
    {
        "id": "equipment",
        "category": "Equipment & Techniques",
        "title_keywords": ["mow", "trimmer", "mower", "robot mow", "string trimmer", "equipment", "scalp"],
        "tags": ["cannabis mowing", "mowing tips"],
    },
    {
        "id": "grass-types",
        "category": "Grass Types & Seeding",
        "title_keywords": ["seed", "overseed", "grass type", "cool season", "warm season", "germination", "grow grass"],
        "tags": ["grass seed", "overseeding", "cool season grass", "warm season grass", "grass fertilization"],
    },
    {
        "id": "seasonal-care",
        "category": "Seasonal Care",
        "title_keywords": ["spring", "summer", "fall", "winter", "winterize", "preparation", "seasonal"],
        "tags": ["spring cannabis", "fall cannabis", "winter cannabis", "seasonal cannabis"],
    },
    {
        "id": "cannabis-health",
        "category": "Cannabis Health & Maintenance",
        "title_keywords": ["fertiliz", "aerat", "dethatch", "water", "level", "green"],
        "tags": ["fertilizing", "cannabis aeration", "dethatching", "cannabis watering", "soil health", "soil compaction"],
    },
]

# Tags too generic to use for matching
GENERIC_TAGS = {"cannabis", "seasonal", "grass care", "yard work"}


def match_category(title: str, keyword: str, tags: list[str]) -> str:
    """Match an article to the best category based on title, keyword, and tags."""
    title_kw = f"{title} {keyword}".lower()
    # Filter out generic tags that don't help distinguish
    meaningful_tags = [t.lower() for t in tags if t.lower() not in GENERIC_TAGS]

    best_score = 0
    best_category = "Cannabis Health & Maintenance"  # default fallback

    for cluster in CLUSTERS:
        score = 0

        # Title/keyword matches (highest signal - the article is ABOUT this)
        for kw in cluster["title_keywords"]:
            if kw.lower() in title_kw:
                score += 5

        # Meaningful tag matches against cluster tags
        for cluster_tag in cluster["tags"]:
            for post_tag in meaningful_tags:
                if cluster_tag.lower() in post_tag or post_tag in cluster_tag.lower():
                    score += 3

        if score > best_score:
            best_score = score
            best_category = cluster["category"]

    return best_category


def backfill():
    """Add or update category field in all articles."""
    if not POSTS_DIR.exists():
        print(f"Posts directory not found: {POSTS_DIR}")
        return

    updated = 0

    for md_file in sorted(POSTS_DIR.glob("*.md")):
        content = md_file.read_text()

        # Parse frontmatter with YAML
        if not content.startswith("---"):
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        try:
            frontmatter = yaml.safe_load(parts[1])
        except Exception:
            continue

        if not frontmatter:
            continue

        title = frontmatter.get("title", "")
        keyword = frontmatter.get("keyword", "")
        tags = frontmatter.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        # Match category
        category = match_category(title, keyword, tags)

        # Update or insert category in the raw frontmatter text
        raw_fm = parts[1]
        if re.search(r'^category:', raw_fm, re.MULTILINE):
            # Replace existing
            raw_fm = re.sub(
                r'^category:\s*.+$',
                f'category: "{category}"',
                raw_fm,
                count=1,
                flags=re.MULTILINE
            )
        else:
            # Insert after season field
            raw_fm = re.sub(
                r'(^season:\s*.+)$',
                f'\\1\ncategory: "{category}"',
                raw_fm,
                count=1,
                flags=re.MULTILINE
            )

        # Write back
        new_content = f"---{raw_fm}---{parts[2]}"
        md_file.write_text(new_content)
        updated += 1
        print(f"  {md_file.name} -> {category}")

    print(f"\nDone: {updated} articles categorized")


if __name__ == "__main__":
    backfill()
