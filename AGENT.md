# AGENT.md - Lawn Care Content Engine

AI-powered content generation system for [lawncare.center](https://lawncare.center).

## Quick Reference

| Item | Value |
|------|-------|
| Live URL | https://lawncare.center |
| Articles | 65 published |
| Cost/article | ~$0.10-0.15 (tracked via cost_tracker.py) |
| Hosting | Vercel (auto-deploy on push to main) |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Content Gen | Python 3, Claude Sonnet, Runware API |

---

## Project Structure

```
lawncare-content-engine/
├── content_generator.py      # Main keyword-first article generation
├── youtube_content_agent.py  # Video-first article generation
├── youtube_search.py         # Video search + AI evaluation + caching
├── affiliate_linker.py       # Amazon affiliate link insertion
├── article_qa.py             # Quality assurance scoring
├── internal_linker.py        # Automatic internal linking between articles
├── rate_limiter.py           # API rate limiting (Claude, Runware, YouTube)
├── regenerate_article.py     # Regenerate existing articles
├── regenerate_images.py      # Image generation utilities
├── gsc_tracker.py            # Google Search Console tracking
├── weekly_content_pipeline.py # Scheduled automation
├── cost_tracker.py           # API cost tracking per article
├── freshness_tracker.py      # Stale article detection
├── content_calendar.py       # Topic balancing & distribution
│
├── .env                      # API keys (never commit)
├── .cache/youtube_cache.json # 30-day video cache
├── drafts/                   # Generated articles before publishing
├── products/
│   └── lawn_care_products.json # 34 affiliate products, 14 categories
│
└── site/                     # Next.js application
    ├── content/posts/        # Published markdown articles
    ├── public/images/articles/ # Generated images
    └── src/
        ├── app/              # App Router pages
        │   ├── articles/     # Article listing + [slug] detail
        │   ├── topics/       # Pillar page with topic clusters
        │   ├── search/       # Search results
        │   └── videos/       # Video gallery
        ├── components/       # React components
        └── lib/
            ├── posts.ts      # Content utilities, shortcode processing
            └── search.ts     # Search algorithms
```

---

## Content Workflows

### Workflow 1: Keyword-First (Default)

```
Keyword → Claude AI → Runware Images → YouTube Videos → Affiliate Links → QA → Draft
```

**Command:**
```bash
python content_generator.py --keyword "how to aerate lawn"
python content_generator.py --keyword "lawn tips" --no-qa  # Skip QA (faster)
```

### Workflow 2: Video-First (YouTube Agent)

```
Trending Video → Transcript → Claude AI → Images → Affiliates → QA → Draft
```

**Commands:**
```bash
python youtube_content_agent.py --dry-run      # Preview candidates
python youtube_content_agent.py                 # Generate 1 article
python youtube_content_agent.py --count 3       # Generate 3 articles
python youtube_content_agent.py --run-pipeline  # Full pipeline
```

---

## Key Commands

```bash
# Generate article
python content_generator.py --keyword "spring lawn care"
python content_generator.py --keyword "spring lawn care" --force  # Skip duplicate check

# Add internal links to all existing articles
python internal_linker.py

# Regenerate existing article
python regenerate_article.py site/content/posts/article-slug.md
python regenerate_article.py site/content/posts/article-slug.md --auto-replace

# Content management tools
python cost_tracker.py --report              # View monthly costs
python freshness_tracker.py --report         # Check for stale articles
python content_calendar.py --analyze         # View topic distribution
python content_calendar.py --gaps            # Find coverage gaps

# Development server
cd site && npm run dev  # http://localhost:3000

# Build & deploy
cd site && npm run build
git add . && git commit -m "Add article" && git push  # Auto-deploys via Vercel
```

---

## Article Frontmatter Schema

```yaml
---
title: "Article Title (55-60 chars)"
slug: "article-slug"
meta_description: "SEO description (145-155 chars)"
keyword: "primary keyword"
featured_image: "/images/articles/slug.jpg"
featured_image_alt: "Hero image description"
section_image: "/images/articles/slug-section.jpg"
section_image_alt: "Section image description"
youtube:
  - id: "VIDEO_ID"
    title: "Video Title"
    channel: "Channel Name"
    position: "hero"
    insights:
      best_quote: "Quote from transcript..."
      key_points: ["Point 1", "Point 2"]
      pro_tips: ["Tip 1", "Tip 2"]
tags: ["lawn care", "seasonal"]
status: "published"
season: "spring"  # spring, summer, fall, winter, year-round
has_affiliate_links: true
affiliate_count: 3
qa_score: 8.6
estimated_read_time: "4 min read"
word_count: 695
generated_at: "2024-12-20"
last_updated: "2024-12-20"

# GEO Optimization Fields (for AI citation)
faqs:
  - question: "Common question about the topic?"
    answer: "Concise, factual answer (2-3 sentences)."
key_stat: "Memorable statistic that can be cited by AI"
tldr: "One-sentence summary of the entire article"
---
```

---

## Image Standards

All images generated via `regenerate_images.py` → `generate_image()`.

| Type | Dimensions | Aspect | Usage |
|------|------------|--------|-------|
| Hero | 1792 × 1024 | 16:9 | Article header |
| Section | 1536 × 1152 | 4:3 | Before "Key Takeaways" |

**Style:** Candid documentary photography
- People actively performing lawn care tasks
- Faces never visible (privacy)
- Seasonal lighting adjustments (spring dew, summer heat, fall colors)

---

## Affiliate Link Rules

**DO insert links in:**
- Article body paragraphs
- Equipment/Tools sections
- Step-by-step instructions mentioning tools

**DO NOT insert links in:**
- YAML frontmatter
- H1 headings
- Sources/References section
- Image alt text
- Already-linked text

**Product database:** `products/lawn_care_products.json`

---

## Environment Variables

**Root `.env`:**
```env
ANTHROPIC_API_KEY=sk-ant-...
RUNWARE_API_KEY=...
YOUTUBE_API_KEY=AIza...
SUPADATA_API_KEY=...           # Transcript fallback
AMAZON_AFFILIATE_TAG=yourname-20
KEYWORDS_EVERYWHERE_API_KEY=... # Optional
```

**`site/.env.local`:**
```env
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

---

## Key Files

| File | Purpose |
|------|---------|
| `content_generator.py` | Main article generation with duplicate detection |
| `youtube_content_agent.py` | Video-first article generation |
| `youtube_search.py` | Video search, AI evaluation, transcript extraction, 30-day caching |
| `affiliate_linker.py` | Affiliate link detection and insertion |
| `article_qa.py` | Quality assurance scoring (8.0+ threshold) |
| `internal_linker.py` | Automatic internal linking between related articles |
| `rate_limiter.py` | Token bucket rate limiting for Claude, Runware, YouTube APIs |
| `regenerate_images.py` | Image generation with Runware API |
| `gsc_tracker.py` | Google Search Console tracking and SEO opportunities |
| `cost_tracker.py` | API cost tracking per article with monthly reports |
| `freshness_tracker.py` | Stale article detection and seasonal refresh alerts |
| `content_calendar.py` | Topic distribution analysis and keyword balancing |
| `site/src/lib/posts.ts` | Content utilities, YouTube shortcode processing |
| `site/src/lib/search.ts` | Search algorithms with relevance scoring |

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
| **Total** | **$0.10-0.15** |

---

## Publishing Flow

1. Generate article → outputs to `drafts/`
2. Review and edit if needed
3. Move to `site/content/posts/`
4. Commit and push → Vercel auto-deploys

```bash
mv drafts/article-slug.md site/content/posts/
git add . && git commit -m "Add article: Title" && git push
```

---

## GitHub Actions

Auto-generates articles on schedule:

| Day | Time | Articles |
|-----|------|----------|
| Monday | 8am UTC | 1 |
| Wednesday | 8am UTC | 1 |

---

## Site Features

- **Search** - Full-text across articles and videos with highlighting
- **Seasonal tabs** - Filter by spring/summer/fall/winter
- **Monthly recommendations** - Dynamic sidebar based on current month
- **Topics pillar page** - `/topics` with 6 topic clusters for SEO
- **Video modal** - YouTube embeds with transcript insights
- **Related articles** - 3 related articles with thumbnails on each article page
- **Animations** - Framer Motion stagger and scroll reveal
- **SEO** - Schema.org markup (Article, FAQPage, BreadcrumbList, VideoObject), meta tags
- **Sitemaps** - Main sitemap, image sitemap, and video sitemap for enhanced indexing
- **GEO optimization** - FAQs, key stats, and TL;DR for AI citation
- **LLM-friendly** - robots.txt allows GPTBot, Claude-Web, PerplexityBot

---

## SEO Tracking (Google Search Console)

Track indexing status and find SEO opportunities using `gsc_tracker.py`.

### Setup (one-time)

1. Create OAuth credentials at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Enable "Google Search Console API" in your GCP project
3. Add yourself as a test user in OAuth consent screen
4. Save credentials as `gsc_credentials.json` in project root

### Usage

```bash
python gsc_tracker.py                    # Full report
python gsc_tracker.py --opportunities    # Focus on quick wins
python gsc_tracker.py --json             # Machine-readable output
python gsc_tracker.py --days 90          # Last 90 days of data
```

### What It Tracks

| Metric | Description |
|--------|-------------|
| Index rate | % of articles indexed by Google |
| Impressions | How often articles appear in search |
| Clicks | Actual visits from search |
| Position | Average ranking position |
| CTR | Click-through rate |

### Opportunities Identified

- **Striking distance** - Keywords ranking 8-20 (push to page 1)
- **Low CTR** - Good rankings but poor click-through (fix titles/meta)
- **Quick wins** - Already ranking well, need content boost

### Current Status (Jan 2026)

| Metric | Value |
|--------|-------|
| Articles indexed | 4 of 63 (6.3%) |
| Total impressions | 109 |
| Total clicks | 1 |
| Best performer | best-time-to-apply-fungicide (pos 10.6) |

Reports saved to `reports/gsc_report_YYYYMMDD.json`

---

## Internal Linking

The `internal_linker.py` script automatically adds contextual links between related articles.

**Features:**
- Analyzes keyword similarity between articles
- Inserts 4-5 links per article at natural insertion points
- Filters generic anchor text ("here", "this", "click")
- Avoids duplicate links and maintains existing ones
- Runs automatically after new article generation

**Usage:**
```bash
python internal_linker.py                    # Update all articles
python internal_linker.py --dry-run          # Preview changes
```

---

## Rate Limiting

The `rate_limiter.py` module prevents API quota exhaustion during batch operations.

**Pre-configured limiters:**
| API | Limiter | Rate |
|-----|---------|------|
| Claude | `claude_limiter` | 50 requests/min |
| Runware | `runware_limiter` | 2 requests/sec |
| YouTube | `youtube_limiter` | 5 requests/5min (burst) |

**Usage in code:**
```python
from rate_limiter import claude_limiter
claude_limiter.wait()  # Blocks until rate allows
```

---

## Duplicate Detection

Content generator checks for duplicate articles before generating:

- Exact keyword match detection
- Slug similarity scoring (>70% triggers warning)
- Word overlap analysis

Use `--force` flag to skip duplicate check:
```bash
python content_generator.py --keyword "spring lawn care" --force
```

---

## Cost Tracking

The `cost_tracker.py` module tracks API costs per article and generates monthly reports.

**Tracked costs:**
| API | What's Tracked |
|-----|----------------|
| Claude | Input/output tokens, estimated cost |
| Runware | Image generation cost (from API response) |
| YouTube | Quota units consumed |

**Usage:**
```bash
python cost_tracker.py --report              # Monthly cost report
python cost_tracker.py --report --month 202601  # Specific month
```

**Output:**
```
📊 Summary:
   Articles generated: 15
   Total cost: $1.85
   Avg per article: $0.12

🤖 Claude API: $1.20 (45,000 tokens)
🎨 Runware: $0.45 (30 images)
📺 YouTube: 2,500 quota units (25% daily)
```

**Storage:** `.logs/costs_YYYYMM.jsonl`

---

## Content Freshness

The `freshness_tracker.py` module detects stale articles needing refresh.

**Checks performed:**
- General staleness (articles >365 days old)
- Seasonal pre-refresh (60 days before season starts)
- Outdated citations (old years in Sources section)

**Usage:**
```bash
python freshness_tracker.py --report         # Full freshness report
python freshness_tracker.py --stale-only     # List only stale articles
python freshness_tracker.py --save           # Save report to file
```

**Output:**
```
📊 Summary:
   Total articles: 65
   Healthy: 60
   Stale (>365 days): 3
   Needs seasonal refresh: 2

🚨 Stale Articles:
   🔴 old-article-slug (450 days)
   🟡 another-article (380 days)

🌱 Seasonal Refresh Needed:
   📆 spring-lawn-care (spring) - 45 days until season
```

**Storage:** `reports/freshness_report_YYYYMMDD.json`

---

## Content Calendar

The `content_calendar.py` module tracks topic distribution and ensures diverse content coverage.

**Features:**
- Analyzes distribution by season, tag category, content type
- Identifies coverage gaps (underrepresented topics)
- Checks keyword similarity to recent articles
- Re-ranks keywords to promote topic diversity

**Usage:**
```bash
python content_calendar.py --analyze         # Full distribution report
python content_calendar.py --gaps            # Show coverage gaps
python content_calendar.py --check "keyword" # Check if keyword is too similar
```

**Output:**
```
📊 CONTENT DISTRIBUTION REPORT
📈 Total Articles: 65

🌱 By Season:
   spring        16 (24.6%) █████
   summer        18 (27.7%) ██████
   fall          15 (23.1%) █████
   winter        16 (24.6%) █████

⚠️  Coverage Gaps:
   🔴 Need more thatch content (only 2 articles)
   🟡 Need more equipment content (only 4 articles)
```

**Integration with keyword research:**
When generating articles, `keyword_research.py` automatically applies balance adjustments to promote topic diversity and avoid publishing similar articles consecutively.

**Storage:** `.cache/topic_distribution.json`

---

## Image Validation

Generated images are automatically validated before saving:

| Check | Threshold | Purpose |
|-------|-----------|---------|
| File size | >10KB | Detect error responses |
| Dimensions | 1000×500 (hero), 800×600 (section) | Ensure usable size |
| Pixel variance | std_dev >10 | Detect blank/uniform images |
| Corruption | PIL load test | Verify file integrity |

Failed images are automatically retried up to 2 times with fresh generation.

---

## SEO Audit

Custom SEO audit skill available in `.skills/skill-seo/`.

**30-Point Audit Checklist:**
| Category | Points | Key Checks |
|----------|--------|------------|
| Title Tag | 4 | 50-60 chars, keyword first, compelling hook |
| Meta Description | 4 | 150-160 chars, action word, specific value |
| Keyword Placement | 5 | Title, description, first 100 words, H2 |
| Content Structure | 6 | Question hook, early code, 1500+ words |
| Featured Snippets | 4 | 40-60 word definitions, numbered steps |
| Internal Linking | 4 | 3-5 links, descriptive anchors |
| Technical SEO | 3 | Single H1, keyword in URL |

**Score interpretation:**
- 27-30 (90%+): Excellent - Ready to publish
- 23-26 (75-89%): Good - Minor optimizations needed
- 17-22 (55-74%): Fair - Several improvements needed
- 0-16 (<55%): Poor - Significant work required

**When to audit:**
- Before publishing new articles
- When optimizing underperforming pages
- After major content updates
