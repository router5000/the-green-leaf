#!/usr/bin/env python3
"""
Batch Regenerate All Articles
Automatically regenerates all articles in site/content/posts/ with:
- QA evaluation
- New Reve images
- Source citations
- Affiliate links
- Automatic backup and cleanup
"""

from pathlib import Path
from regenerate_article import regenerate_multiple

# Find all articles in posts directory
posts_dir = Path("site/content/posts")
articles = sorted(posts_dir.glob("*.md"))

# Filter out any backup or temp files
articles = [a for a in articles if not a.stem.endswith("-NEW") and not a.stem.endswith("_backup")]

print(f"Found {len(articles)} articles to regenerate")
print("\nArticles:")
for i, article in enumerate(articles, 1):
    print(f"  {i}. {article.stem}")

print("\n" + "="*60)
print("⚠️  This will:")
print("  1. Backup all old articles to site/content/posts_backups/")
print("  2. Regenerate with QA system")
print("  3. Replace old articles with new versions")
print("  4. Use same slugs (URLs won't change)")
print("="*60)

response = input("\nProceed with regeneration? (yes/no): ").strip().lower()

if response == "yes":
    print("\n🚀 Starting batch regeneration...")
    print("⏱️  Estimated time: ~2-3 minutes per article")
    print(f"📊 Total time: ~{len(articles) * 2.5 / 60:.1f} hours\n")

    succeeded, failed = regenerate_multiple(
        articles,
        enable_qa=True,
        auto_replace=True  # Auto-replace without prompting each time
    )

    print("\n🎉 Batch regeneration complete!")
    print(f"✅ {len(succeeded)} articles successfully regenerated")
    print(f"❌ {len(failed)} articles failed")

    if failed:
        print("\n⚠️  Failed articles (try regenerating manually):")
        for article in failed:
            print(f"  python3 regenerate_article.py {article}")
else:
    print("\n⏸️  Regeneration cancelled")
