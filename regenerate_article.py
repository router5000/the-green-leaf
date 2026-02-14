#!/usr/bin/env python3
"""
Smart Article Regeneration Script
- Extracts keyword from old article
- Generates new version with QA system
- Backs up old article
- Replaces with new version using same slug
- Cleans up backup after confirmation
"""

import os
import sys
import shutil
import json
import re
from pathlib import Path
from datetime import datetime
from content_generator import generate_article, save_to_notion_format, save_article_json


def extract_keyword_from_article(article_path: Path) -> str:
    """Extract the keyword from an existing article's frontmatter."""
    with open(article_path) as f:
        content = f.read()

    # Extract keyword from frontmatter
    match = re.search(r'keyword:\s*"([^"]+)"', content)
    if match:
        return match.group(1)

    raise ValueError(f"Could not find keyword in {article_path}")


def backup_old_article(article_path: Path, backup_dir: Path):
    """Backup the old article before replacement."""
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{article_path.stem}_{timestamp}.md"
    backup_path = backup_dir / backup_name

    shutil.copy2(article_path, backup_path)
    print(f"   📦 Backed up old article: {backup_path}")
    return backup_path


def regenerate_article_smart(article_path: Path, enable_qa: bool = True, auto_replace: bool = False):
    """
    Intelligently regenerate an article:
    1. Extract keyword from old article
    2. Generate new version with QA
    3. Backup old version
    4. Replace old with new (using same slug)
    5. Clean up
    """

    article_path = Path(article_path)

    if not article_path.exists():
        print(f"❌ Article not found: {article_path}")
        return False

    print(f"\n🔄 Regenerating: {article_path.name}")
    print("="*60)

    # Step 1: Extract keyword
    try:
        keyword = extract_keyword_from_article(article_path)
        print(f"📌 Keyword: {keyword}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False

    # Step 2: Generate new article
    print(f"🤖 Generating new version with QA...")
    try:
        article = generate_article(keyword, enable_qa=enable_qa)
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

    # Show QA results
    if enable_qa and article.get('qa_evaluation'):
        qa_score = article['qa_evaluation']['scores']['overall']
        print(f"   📊 QA Score: {qa_score:.1f}/10")
        if article.get('qa_passed'):
            print(f"   ✅ Quality threshold passed!")
        else:
            print(f"   ⚠️  Needs manual review")

    # IMPORTANT: Preserve original slug from filename (don't use Claude's generated slug)
    original_slug = article_path.stem
    article['slug'] = original_slug

    print(f"   ✅ New article generated ({article['word_count']} words)")

    # Step 3: Backup old article
    backup_dir = Path("site/content/posts_backups")
    backup_path = backup_old_article(article_path, backup_dir)

    # Step 4: Save new article
    temp_path = Path("drafts") / f"{article['slug']}.md"
    save_to_notion_format(article, output_dir="drafts")
    save_article_json(article, output_dir="drafts/json")

    # Step 5: Replace old article with new one
    if auto_replace:
        replace = True
    else:
        print(f"\n⚠️  Ready to replace old article with new version")
        print(f"   Old: {article_path}")
        print(f"   New: {temp_path}")
        response = input("   Replace? (y/n): ").strip().lower()
        replace = response == 'y'

    if replace:
        # Copy new article to replace old one
        shutil.copy2(temp_path, article_path)
        print(f"   ✅ Replaced: {article_path}")

        # Remove temp file
        temp_path.unlink()
        print(f"   🧹 Cleaned up temp file")

        print(f"\n✅ SUCCESS! Article regenerated and replaced")
        print(f"   Backup: {backup_path}")
        print(f"   Live: {article_path}")

        # Show comparison
        print(f"\n📊 Comparison:")
        print(f"   Old → New")
        print(f"   {backup_path.stat().st_size} bytes → {article_path.stat().st_size} bytes")

        return True
    else:
        print(f"   ⏸️  Skipped replacement. New version in: {temp_path}")
        return False


def regenerate_multiple(article_paths: list, enable_qa: bool = True, auto_replace: bool = False):
    """Regenerate multiple articles with rate limiting."""
    import time

    total = len(article_paths)
    succeeded = []
    failed = []

    print(f"\n🌱 Regenerating {total} articles")
    print("="*60)

    for i, article_path in enumerate(article_paths, 1):
        print(f"\n[{i}/{total}]")

        success = regenerate_article_smart(article_path, enable_qa, auto_replace)

        if success:
            succeeded.append(article_path)
        else:
            failed.append(article_path)

        # Rate limiting between articles
        if i < total:
            print(f"\n⏳ Waiting 60 seconds for rate limits...")
            time.sleep(60)

    # Summary
    print("\n" + "="*60)
    print(f"📊 SUMMARY")
    print("="*60)
    print(f"✅ Succeeded: {len(succeeded)}/{total}")
    print(f"❌ Failed: {len(failed)}/{total}")

    if failed:
        print(f"\nFailed articles:")
        for path in failed:
            print(f"  - {path}")

    return succeeded, failed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Regenerate articles with automatic cleanup and replacement"
    )
    parser.add_argument(
        "articles",
        nargs="+",
        help="Article file(s) to regenerate (paths or glob patterns)"
    )
    parser.add_argument(
        "--no-qa",
        action="store_true",
        help="Disable QA pipeline (faster)"
    )
    parser.add_argument(
        "--auto-replace",
        action="store_true",
        help="Automatically replace without prompting"
    )

    args = parser.parse_args()

    # Determine QA setting
    enable_qa = not args.no_qa

    # Expand glob patterns if any
    article_paths = []
    for pattern in args.articles:
        if "*" in pattern:
            article_paths.extend(Path().glob(pattern))
        else:
            article_paths.append(Path(pattern))

    if not article_paths:
        print("❌ No articles found")
        sys.exit(1)

    # Single or multiple?
    if len(article_paths) == 1:
        regenerate_article_smart(article_paths[0], enable_qa, args.auto_replace)
    else:
        regenerate_multiple(article_paths, enable_qa, args.auto_replace)
