#!/usr/bin/env python3
"""
Backfill category field into article frontmatter.
Uses the same topic cluster matching logic as the topics page.
"""

import re
from pathlib import Path

import yaml

POSTS_DIR = Path("site/content/posts")

# Topic clusters — aligned with the six Topics page cards
CLUSTERS = [
    {
        "id": "strains-genetics",
        "category": "strains-genetics",
        "title_keywords": [
            "strain", "indica", "sativa", "hybrid", "genetics", "phenotype", "terpene",
            "lineage", "kush", "haze", "diesel", "cookies", "gelato", "runtz", "zkittlez",
            "wedding cake", "blue dream", "og kush", "northern lights", "granddaddy",
            "sour diesel", "purple punch", "white widow", "bubba kush", "mac 1",
            "do-si-dos", "mimosa", "biscotti", "best strains", "strains for", "top strains",
        ],
        "tags": [
            "strain profile", "strain guide", "strain review", "strain effects",
            "indica", "sativa", "hybrid", "terpene profiles", "cannabis strains",
        ],
    },
    {
        "id": "growing-cultivation",
        "category": "growing-cultivation",
        "title_keywords": [
            "grow", "cultivat", "indoor", "outdoor", "hydroponic", "soil", "nutrient",
            "light", "flower", "veg", "harvest", "germinate", "seed", "clone",
            "tent", "yield", "pruning", "training", "lst", "scrog", "topping",
            "fimming", "compost", "autoflower", "ph level",
        ],
        "tags": [
            "growing cannabis", "indoor growing", "outdoor growing", "hydroponics",
            "nutrients", "cannabis cultivation",
        ],
    },
    {
        "id": "consumption-methods",
        "category": "consumption-methods",
        "title_keywords": [
            "smoke", "vape", "edible", "tincture", "topical", "dab", "concentrate",
            "pre-roll", "joint", "blunt", "bong", "pipe", "hash", "rosin", "live resin",
            "consumption methods", "vaping vs", "edibles vs", "budtender", "dispensary menu",
            "tolerance break",
        ],
        "tags": [
            "edibles", "vaping", "tinctures", "concentrates", "topicals",
            "consumption methods",
        ],
    },
    {
        "id": "health-wellness",
        "category": "health-wellness",
        "title_keywords": [
            "anxiety", "pain", "sleep", "depression", "ptsd", "inflammation",
            "medical", "nausea", "migraine", "arthritis", "wellness", "therapeutic",
            "cbd", "health benefit", "chronic pain", "insomnia", "stress relief",
            "mental health", "cancer", "seizure",
        ],
        "tags": [
            "CBD", "medical cannabis", "wellness", "pain relief", "anxiety",
            "health benefits",
        ],
    },
    {
        "id": "legal-industry",
        "category": "legal-industry",
        "title_keywords": [
            "legal", "law", "regulat", "licens", "federal", "legislat", "policy",
            "decriminalize", "possession", "legalization", "adult-use", "industry",
            "hemp", "farm bill", "dispensary license", "cannabis business",
        ],
        "tags": [
            "cannabis law", "legalization", "regulations", "dispensary",
            "cannabis industry",
        ],
    },
    {
        "id": "culture-lifestyle",
        "category": "culture-lifestyle",
        "title_keywords": [
            "histor", "recipe", "cook", "event", "festival", "travel", "accessor",
            "culture", "lifestyle", "celebrity", "art", "music", "movie",
            "documentary", "etiquette", "paraphernalia",
        ],
        "tags": [
            "cannabis culture", "recipes", "cannabis history", "accessories",
            "lifestyle",
        ],
    },
]

# Tags too generic to use for matching
GENERIC_TAGS = {"cannabis", "marijuana", "weed", "pot"}


def match_category(title: str, keyword: str, tags: list[str]) -> str:
    """Match an article to the best category based on title, keyword, and tags."""
    title_kw = f"{title} {keyword}".lower()
    # Filter out generic tags that don't help distinguish
    meaningful_tags = [t.lower() for t in tags if t.lower() not in GENERIC_TAGS]

    best_score = 0
    best_category = "strains-genetics"  # default fallback

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
