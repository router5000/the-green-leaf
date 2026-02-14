# Learnings & Lessons Learned

This document captures key learnings from developing and maintaining the Lawn Care Content Engine.

---

## YouTube Content Agent Implementation

### 1. YouTube Transcript API Version Changes

**Problem:** The `youtube-transcript-api` library changed its API in v1.x

| Old API (v0.x) | New API (v1.x) |
|----------------|----------------|
| `YouTubeTranscriptApi.get_transcript(video_id)` | `YouTubeTranscriptApi().fetch(video_id)` |
| `YouTubeTranscriptApi.list_transcripts(video_id)` | `YouTubeTranscriptApi().list(video_id)` |
| Class methods | Instance methods (requires instantiation) |
| Returns `list[dict]` with `entry["text"]` | Returns objects with `entry.text` attribute |

**Solution:**
```python
# Correct usage for v1.x
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id)
full_text = " ".join([entry.text for entry in transcript])
```

**Lesson:** Always check library documentation when encountering AttributeError on well-known methods.

---

### 2. Transcript Availability is Limited

**Problem:** Most YouTube videos don't have accessible transcripts via the API.

**Observations:**
- Auto-generated captions are often not available via API
- Many creators don't enable manual captions
- Out of ~50 candidate videos, often only 1-2 have accessible transcripts

**Mitigations:**
- Search broader (more queries, lower view thresholds)
- Target channels known to have transcripts
- Consider adding `--video-id` flag for manual video selection
- Accept that this workflow has lower throughput than keyword-first

---

### 3. Python Global Variable Scope

**Problem:** SyntaxError when using `global` after the variable is referenced in default arguments.

```python
# WRONG - causes SyntaxError
def main():
    parser.add_argument("--min-views", default=MIN_VIEWS)  # MIN_VIEWS used here
    args = parser.parse_args()
    global MIN_VIEWS  # Error: used before global declaration
    MIN_VIEWS = args.min_views
```

**Solution:** Don't use global, or restructure:
```python
# Option 1: Hardcode default
parser.add_argument("--min-views", default=10000)

# Option 2: Pass as parameter instead of global
```

---

## Frontmatter & YAML Parsing

### 4. YAML Quote Handling in Regex

**Problem:** QA parser used regex that only matched double quotes, but YAML often uses single quotes.

```python
# WRONG - only matches "title"
title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)

# Article had:
title: 'Dallas Grass vs Crabgrass...'  # Single quotes - no match!
```

**Solution:** Use proper YAML parsing:
```python
import yaml
fm_data = yaml.safe_load(frontmatter)
title = fm_data.get('title', 'Default')
```

**Lesson:** Always use proper parsers (YAML, JSON) instead of regex for structured data.

---

### 5. Required Frontmatter Fields

**Problem:** Build failed with `Cannot read properties of undefined (reading 'toUpperCase')` because article was missing `season` field.

**Required fields for articles:**
```yaml
title: "..."
slug: "..."
meta_description: "..."
keyword: "..."
featured_image: "..."
featured_image_alt: "..."
section_image: "..."        # Optional but recommended
section_image_alt: "..."    # Optional but recommended
season: "spring|summer|fall|winter"  # REQUIRED - used on homepage
status: "draft|published"
tags: [...]
```

**Lesson:** When adding new article sources, ensure all required fields are populated. Check homepage/templates for field usage.

---

## API & Integration Issues

### 6. Google API Python Version Warnings

**Observation:** Python 3.9 triggers deprecation warnings from Google API:
```
FutureWarning: You are using a Python version (3.9.6) past its end of life
```

Also see:
```
An error occurred: module 'importlib.metadata' has no attribute 'packages_distributions'
```

**Impact:** Warnings only - functionality still works. Can be suppressed or ignored.

**Long-term fix:** Upgrade to Python 3.10+

---

### 7. Affiliate Linker Usage

**Problem:** Running `python affiliate_linker.py file.md` just runs a test demo, doesn't process the file.

**Correct usage:** The affiliate linker is designed to be called as a module:
```python
from affiliate_linker import process_article_for_affiliates

content = Path('article.md').read_text()
# Split frontmatter and body
result = process_article_for_affiliates(body_content, max_links=5)
# result['content'] has the modified content
# result['link_count'] has number of links added
```

**Lesson:** Check how modules are designed to be used (function vs CLI) before calling them.

---

## Deployment & Build

### 8. Vercel Deployment Debugging

**Tools available:**
```bash
# List recent deployments
vercel ls

# Inspect specific deployment
vercel inspect <deployment-url>

# View logs (only works for successful deployments)
vercel logs <deployment-url>
```

**For failed deployments:** Run local build to see errors:
```bash
cd site && npm run build
```

**Lesson:** Vercel logs aren't available for errored deployments. Always test locally first.

---

### 9. Next.js Static Generation Errors

**Pattern:** Errors during static page generation often indicate:
1. Missing data in content files (frontmatter fields)
2. Null/undefined values being passed to string methods
3. File parsing errors

**Debugging approach:**
1. Check the error message for which page failed (`Error occurred prerendering page "/"`)
2. Search codebase for the method mentioned (`.toUpperCase()`)
3. Trace back to find what data is undefined
4. Check recent content changes for missing fields

---

## Code Quality

### 10. Image Generation Integration

**Correct way to generate images for existing articles:**
```python
from content_generator import generate_hero_image, generate_section_image

keyword = 'article keyword'
slug = 'article-slug'
season = 'summer'

generate_hero_image(keyword, slug, season)
generate_section_image(keyword, slug, season, 'Section Title')
```

**Images saved to:** `site/public/images/articles/{slug}.jpg` and `{slug}-section.jpg`

---

## Process Improvements

### 11. Article Generation Checklist

Before publishing any article (from any source):

- [ ] All required frontmatter fields present
- [ ] `season` field set correctly
- [ ] `status` set to `published` (not `draft`)
- [ ] Images generated and saved
- [ ] Affiliate links processed
- [ ] Local build passes (`npm run build`)
- [ ] Commit and push
- [ ] Verify Vercel deployment succeeds

### 12. Testing New Features

When adding new article generation methods:

1. **Generate draft** - Don't auto-publish
2. **Verify frontmatter** - Check all required fields
3. **Local build test** - Run `npm run build` before pushing
4. **Incremental commits** - Commit fixes separately for easy rollback

---

## Quick Reference

### Common Commands

```bash
# YouTube Agent
python youtube_content_agent.py --dry-run          # Preview videos
python youtube_content_agent.py                     # Generate 1 article
python youtube_content_agent.py --run-pipeline     # Full pipeline

# Build & Deploy
cd site && npm run build                           # Local build test
vercel ls                                          # Check deployments

# QA
python article_qa.py --test path/to/article.md    # Run QA on article

# Images (in Python)
from content_generator import generate_hero_image, generate_section_image
```

### File Locations

| Content | Location |
|---------|----------|
| Published articles | `site/content/posts/` |
| Draft articles | `drafts/` |
| Article images | `site/public/images/articles/` |
| Affiliate products | `products/lawn_care_products.json` |
| YouTube cache | `.cache/youtube_agent/` |

---

*Last updated: 2025-12-27*
