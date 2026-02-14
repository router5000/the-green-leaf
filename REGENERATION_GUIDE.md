# Article Regeneration Guide
## Smart Cleanup & Replacement Process

**Updated:** December 7, 2025
**Purpose:** Regenerate old articles with QA system, YouTube videos, Runware images, and seamless replacement

---

## What This Does

The regeneration scripts automatically:
1. Extract keyword from old article
2. Generate new version with QA system
3. Generate Runware images (hero + section)
4. Search and embed relevant YouTube videos
5. Insert affiliate links
6. Backup old article with timestamp
7. Replace old article with new version (same slug/URL)
8. Clean up temporary files

**No manual file management needed!**

---

## Quick Start

### Regenerate Single Article
```bash
python3 regenerate_article.py site/content/posts/how-often-should-i-aerate-my-lawn.md
```

### Regenerate All Articles
```bash
python3 regenerate_all_articles.py
```

That's it! The system handles everything.

---

## Command Options

### Single Article Regeneration

```bash
# Basic regeneration (with QA, prompts for confirmation)
python3 regenerate_article.py site/content/posts/article-name.md

# Skip QA (faster, lower cost)
python3 regenerate_article.py site/content/posts/article-name.md --no-qa

# Auto-replace without confirmation prompt
python3 regenerate_article.py site/content/posts/article-name.md --auto-replace

# Combine options
python3 regenerate_article.py site/content/posts/article-name.md --no-qa --auto-replace
```

### Multiple Articles with Glob Pattern

```bash
# Regenerate all articles starting with "best-time"
python3 regenerate_article.py site/content/posts/best-time-*.md

# Regenerate all articles
python3 regenerate_article.py site/content/posts/*.md --auto-replace
```

---

## What Happens During Regeneration

### Step-by-Step Process:

```
🔄 Regenerating: how-often-should-i-aerate-my-lawn.md
============================================================
📌 Keyword: how often should I aerate my lawn
🤖 Generating new version with QA...
   🎨 Generating hero image (Runware)...
   ✅ Image saved: hero.jpg (310 KB)
   🎨 Generating section image (Runware)...
   ✅ Image saved: section.jpg (245 KB)
   🔍 Running quality assurance...
   📊 QA Score: 8.2/10
   ✅ Quality threshold passed!
   🔗 Adding affiliate links...
   ✅ Inserted 3 affiliate links
   📺 Searching for YouTube videos...
   ✅ Found 2 relevant videos (scores: 10, 9)
   ✅ New article generated (695 words)
📦 Backed up old article: posts_backups/article_20251207_140530.md
⚠️  Ready to replace old article with new version
   Replace? (y/n): y
   ✅ Replaced: site/content/posts/how-often-should-i-aerate-my-lawn.md
   🧹 Cleaned up temp file

✅ SUCCESS! Article regenerated and replaced
```

---

## What Gets Generated

### Each Regenerated Article Includes:

| Feature | Description |
|---------|-------------|
| **Content** | 600-750 words, SEO-optimized |
| **Hero Image** | 1792x1024 landscape (Runware) |
| **Section Image** | 1024x1024 square (Runware) |
| **Hero Video** | YouTube embed after title |
| **Section Video** | YouTube embed in last third |
| **Affiliate Links** | 3-5 Amazon links (open in new tab) |
| **Sources** | 4-6 clickable numbered citations |
| **QA Score** | Automated quality evaluation |

### Frontmatter Structure:

```yaml
---
title: "How Often Should You Aerate Your Lawn?"
meta_description: "Learn the optimal lawn aeration..."
slug: "how-often-should-i-aerate-my-lawn"
keyword: "how often should I aerate my lawn"
featured_image: "/images/articles/how-often-aerate.jpg"
featured_image_alt: "Professional photograph of lawn aeration"
section_image: "/images/articles/how-often-aerate-section.jpg"
section_image_alt: "Detail view of aeration process"
youtube:
  - id: "abc123xyz"
    title: "How to Aerate Your Lawn"
    channel: "The Lawn Care Nut"
    position: "hero"
  - id: "def456uvw"
    title: "Aeration Tips"
    channel: "Ryan Knorr"
    position: "section"
tags: ["aeration", "lawn care", "fall"]
status: "draft"
generated_at: "2025-12-07"
season: "fall"
estimated_read_time: "4 min read"
word_count: 695
has_affiliate_links: true
affiliate_count: 3
qa_score: 8.2
qa_passed: true
---
```

---

## File Structure After Regeneration

```
lawncare-content-engine/
├── site/content/
│   ├── posts/
│   │   ├── article-1.md        ← NEW version (replaced)
│   │   └── ...
│   └── posts_backups/
│       ├── article-1_20251207_140530.md  ← OLD backup
│       └── ...
├── site/public/images/articles/
│   ├── article-1.jpg           ← Hero image (Runware)
│   ├── article-1-section.jpg   ← Section image (Runware)
│   └── ...
└── drafts/
    └── (temporary files cleaned up)
```

---

## Cost Per Article

| Component | Cost |
|-----------|------|
| Text generation (Claude) | $0.02-0.05 |
| QA evaluation (Claude) | $0.02-0.03 |
| Hero image (Runware) | ~$0.02 |
| Section image (Runware) | ~$0.02 |
| Video evaluation (Claude) | $0.01-0.02 |
| YouTube API | Free |
| Affiliate detection | $0.01 |
| **Total per article** | **$0.10-0.15** |

**For 37 articles: ~$5-6 total**

---

## Time Estimates

### Single Article
- Generation: 2-3 minutes
- Manual confirmation: 10 seconds
- **Total: ~3 minutes**

### All 37 Articles
- Generation: 2.5 min × 37 = 93 minutes
- Rate limiting: 60 sec × 36 = 36 minutes
- **Total: ~2 hours** (mostly automated)

---

## Safety Features

### Automatic Backups
Every old article is backed up with timestamp:
```
posts_backups/article-name_20251207_140530.md
```

### Rollback Process
If you need to revert:
```bash
# Find your backup
ls site/content/posts_backups/

# Restore it
cp site/content/posts_backups/article_20251207_140530.md \
   site/content/posts/article.md
```

### Dry Run Mode
Want to test without replacing?
```bash
# Generate but don't replace (respond 'n' to prompt)
python3 regenerate_article.py site/content/posts/article.md
# Then check drafts/article.md
```

---

## Troubleshooting

### "Rate limit error"
**Solution:** Wait 60 seconds and retry
```bash
sleep 60 && python3 regenerate_article.py site/content/posts/article.md
```

### "YouTube videos not found"
**Solution:**
- Check YOUTUBE_API_KEY in .env
- Try lowering min_score to 6.0
- Broader keywords find more videos

### "QA score too low"
**Solution:** Article flagged for manual review
- Check `drafts/qa_logs/feedback_DATE.jsonl`
- Article still generated and replaced
- Just needs manual check

### Want to revert?
**Solution:** Restore from backup
```bash
cp site/content/posts_backups/article_DATE.md \
   site/content/posts/article.md
```

---

## Pro Tips

1. **Test with one article first**
   ```bash
   python3 regenerate_article.py site/content/posts/best-time-to-aerate-lawn.md
   ```

2. **Skip QA for faster regeneration**
   ```bash
   python3 regenerate_article.py site/content/posts/article.md --no-qa
   ```

3. **Preview locally before deploying**
   ```bash
   cd site && npm run dev
   # Visit http://localhost:3000/articles/article-slug
   ```

4. **Verify after regeneration**
   - Check article page loads
   - Verify both videos play
   - Check images render
   - Test affiliate links open in new tab
   - Confirm sources are clickable

---

## Ready to Regenerate!

**Single article test:**
```bash
python3 regenerate_article.py site/content/posts/how-often-should-i-aerate-my-lawn.md
```

**All articles:**
```bash
python3 regenerate_all_articles.py
```

The system handles everything automatically!
