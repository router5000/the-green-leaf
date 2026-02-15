# The Green Leaf Content Engine - Project Overview & Updates

**Last Updated:** January 2026
**Project Status:** PRODUCTION - FULLY AUTOMATED
**Current Season:** Winter
**Live Site:** https://thegreenleaf.com
**GitHub:** https://github.com/JakeTaylorDesign/cannabiscare-center

---

## Project Overview

An AI-powered, fully automated content generation and publishing system for **thegreenleaf.com**. Generates SEO-optimized cannabis articles using Claude AI with Runware-generated photorealistic images, YouTube video embeds, and Amazon affiliate links. Content is published automatically via GitHub Actions on a Monday/Wednesday schedule.

### Core Capabilities
- Automated keyword research via Google Trends with seasonal balancing
- Article generation with Claude Sonnet 4 (600-750 words, optimized for engagement)
- Dual photorealistic image generation via Runware AI (hero 16:9 + section 4:3)
- YouTube video discovery, transcript analysis, and embedding
- Amazon affiliate link insertion from curated 34-product database
- Multi-dimensional QA scoring with auto-refinement
- Internal cross-article linking for SEO
- Automated git commit/push triggering Vercel deployment
- Content freshness tracking and article regeneration
- Cost tracking per article (~$0.10-0.15 each)

---

## Technology Stack

### Backend (Content Generation)
- **Language:** Python 3.11 (CI) / 3.9.6 (local)
- **AI Model:** Claude Sonnet 4 (`claude-sonnet-4-20250514`) - Text generation & QA
- **Image Generation:** Runware AI (`runware:100@1`) - Photorealistic documentary-style images
- **APIs:**
  - Anthropic Python SDK - Content generation & evaluation
  - Runware API - Image generation
  - YouTube Data API v3 - Video search
  - youtube-transcript-api + SupaData - Transcript extraction
  - Google Trends (pytrends) - Keyword research
  - Google Search Console API - SEO tracking
- **Key Dependencies:**
  - `anthropic` - AI content generation
  - `requests` - HTTP client
  - `python-dotenv` - Environment config
  - `Pillow` - Image processing
  - `PyYAML` - Config parsing
  - `google-api-python-client` - YouTube API
  - `youtube-transcript-api` - Transcripts
  - `pytrends` - Google Trends
  - `google-auth-oauthlib` - Search Console auth

### Frontend (Website)
- **Framework:** Next.js 16.1.1 (App Router)
- **Runtime:** React 19.2.3
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS 3.3.0 + @tailwindcss/typography
- **Content Processing:**
  - `gray-matter` - Parse markdown frontmatter
  - `remark` + `remark-html` - Markdown to HTML
- **Animations:** Framer Motion 12.23.26
- **Analytics:** PostHog JS SDK
- **Build:** Static site generation (SSG), standalone output
- **Deployment:** Vercel (auto-deploys on push to main)
- **Domain:** thegreenleaf.com (Hostinger DNS → Vercel)

---

## Project Structure

```
cannabiscare-content-engine/
├── content_generator.py         # Main article generation engine (48KB)
├── youtube_content_agent.py     # Video-first article generation (35KB)
├── weekly_content_pipeline.py   # Pipeline orchestration (10KB)
├── affiliate_linker.py          # Amazon affiliate link insertion (9KB)
├── article_qa.py                # Quality assurance scoring (22KB)
├── internal_linker.py           # Cross-article SEO linking (17KB)
├── youtube_search.py            # Video search + transcript caching (24KB)
├── keyword_research.py          # Google Trends keyword selection (17KB)
├── content_calendar.py          # Topic balancing & distribution (14KB)
├── cost_tracker.py              # API cost tracking (10KB)
├── freshness_tracker.py         # Stale article detection (12KB)
├── gsc_tracker.py               # Google Search Console tracking (13KB)
├── regenerate_article.py        # Article refresh utility (7KB)
├── regenerate_images.py         # Image regeneration (13KB)
├── auto_publish.py              # Git automation (9KB)
├── rate_limiter.py              # API throttling (5KB)
├── requirements.txt             # Python dependencies
├── .env                         # API keys (gitignored)
│
├── products/
│   └── cannabis_products.json  # 34 affiliate products, 14 categories
│
├── drafts/                      # Generated articles awaiting review
│   ├── *.md                     # Draft markdown files
│   └── batch_summary.json       # Generation batch metadata
│
├── .github/workflows/
│   └── weekly-content.yml       # CI/CD: Mon & Wed @ 8am UTC
│
├── .cache/                      # Keyword & YouTube caches
├── .logs/                       # Pipeline & cost logs
├── reports/                     # GSC analytics exports
│
└── site/                        # Next.js application
    ├── content/posts/           # 66 published markdown articles
    ├── public/
    │   ├── images/articles/     # 158 generated images
    │   ├── robots.txt           # AI & search crawler permissions
    │   └── llms.txt             # LLM access file
    ├── src/
    │   ├── app/                 # Next.js App Router pages
    │   │   ├── page.tsx         # Home (featured posts grid)
    │   │   ├── articles/        # Article listing + detail pages
    │   │   ├── videos/          # YouTube video gallery
    │   │   ├── topics/          # Topic cluster/pillar pages
    │   │   ├── search/          # Full-text search
    │   │   ├── privacy-policy/
    │   │   ├── terms-of-service/
    │   │   ├── affiliate-disclosure/
    │   │   ├── sitemap.ts       # XML sitemap
    │   │   ├── image-sitemap.xml/route.ts
    │   │   ├── video-sitemap.xml/route.ts
    │   │   └── layout.tsx       # Root layout + SEO metadata
    │   ├── components/          # React components
    │   │   ├── ArticleContent.tsx
    │   │   ├── ArticlesTabs.tsx
    │   │   ├── HomeContent.tsx
    │   │   ├── SearchBar.tsx / SearchResults.tsx
    │   │   ├── VideoModal.tsx / VideosGrid.tsx / VideosTabs.tsx
    │   │   ├── MobileNav.tsx
    │   │   ├── PostHogProvider.tsx
    │   │   └── HeaderContext.tsx
    │   └── lib/
    │       ├── posts.ts         # Markdown parsing utilities
    │       └── search.ts        # Relevance scoring algorithm
    ├── package.json
    ├── tailwind.config.js       # Custom "grass" color palette
    ├── next.config.js           # Standalone output, image proxying
    └── vercel.json              # Region, redirects (www stripping)
```

---

## Content Generation Pipeline

### Full Workflow
```
Keyword Research (Google Trends + seasonal balancing)
    ↓
Content Generation (Claude Sonnet 4, 600-750 words)
    ↓
Image Generation (Runware AI, hero 16:9 + section 4:3)
    ↓
YouTube Video Search & Embedding (transcript analysis)
    ↓
Affiliate Link Insertion (Amazon Associates, max 5/article)
    ↓
Internal Linking (cross-article SEO links)
    ↓
Quality Assurance (multi-dimensional scoring, auto-refinement)
    ↓
Git Commit & Push → Vercel Auto-Deployment
```

### Article Structure
Each generated article includes:
- **Quick Answer** section (2-3 sentence direct answer)
- **Key Takeaways** bulleted list
- **Hero Image** (1792x1024, 16:9 landscape)
- **Section Image** (1536x1152, 4:3) inserted before 2nd H2
- SEO-optimized title (55-60 chars) and meta description (145-155 chars)
- H2/H3 heading hierarchy with keyword optimization
- Embedded YouTube videos with key quotes and pro tips
- Amazon affiliate links (contextual, max 5 per article)
- Source citations (university extensions, USDA)
- Internal links to related articles

### Image Style
- Candid documentary-style photographs
- Person performing cannabis tasks (shot from behind/side, no faces)
- Professional DSLR quality (Canon EOS R5 aesthetic)
- Natural lighting with seasonal variations
- Activity-specific prompts (mowing, aerating, fertilizing, etc.)

---

## Current Content Stats

| Metric | Count |
|--------|-------|
| Published articles | 66 |
| Generated images | 158 |
| Affiliate products | 34 (14 categories) |
| Embedded YouTube videos | 132+ |
| Draft articles | 35+ |

---

## Automation Schedule

**GitHub Actions Workflow:** `.github/workflows/weekly-content.yml`

| Trigger | Schedule |
|---------|----------|
| Automatic | Monday & Wednesday @ 8am UTC (3am EST) |
| Manual | Via GitHub Actions UI with custom inputs |

**Manual Dispatch Options:**
- `keyword` - Specific keyword to target
- `count` - Number of articles (default: 1)
- `season` - Force season (spring/summer/fall/winter/evergreen/auto)
- `skip_qa` - Skip QA for faster generation
- `dry_run` - Preview without changes

---

## Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` - Claude API access
- `RUNWARE_API_KEY` - Image generation
- `YOUTUBE_API_KEY` - Video discovery
- `AMAZON_AFFILIATE_TAG` - Affiliate program (amazonlinkp00-20)

**Optional:**
- `SUPADATA_API_KEY` - YouTube transcript fallback
- `KEYWORDS_EVERYWHERE_API_KEY` - Search volume data
- `NOTIFICATION_WEBHOOK_URL` - Discord/Slack failure alerts

---

## Site Features

### Pages
| Route | Purpose |
|-------|---------|
| `/` | Home - Featured article + monthly posts grid |
| `/articles` | Tabbed article listing with thumbnails |
| `/articles/[slug]` | Full article with images, videos, affiliate links |
| `/videos` | YouTube video gallery grouped by channel |
| `/topics` | Topic cluster/pillar pages |
| `/search?q=...` | Full-text search with relevance scoring |
| `/privacy-policy` | GDPR/CCPA compliant |
| `/terms-of-service` | Legal protection |
| `/affiliate-disclosure` | FTC compliant |

### SEO & Optimization
- XML sitemap (auto-generated from articles)
- Image sitemap and video sitemap
- JSON-LD structured data (Article, Breadcrumb, ImageObject)
- Open Graph and Twitter Card tags
- robots.txt welcoming AI crawlers (GPTBot, Claude-Web, PerplexityBot)
- Semantic HTML5 structure with ARIA labels
- PostHog analytics integration

---

## Cost Analysis

### Per Article
| Component | Cost |
|-----------|------|
| Claude text generation | $0.02-0.05 |
| Runware images (2) | $0.04-0.06 |
| QA evaluation | $0.02-0.03 |
| Video evaluation | $0.01-0.02 |
| Affiliate detection | $0.01 |
| **Total** | **$0.10-0.15** |

### Monthly (current schedule: 2 articles/week)
- API costs: ~$0.80-1.20/month
- Vercel hosting: Free
- Domain: Owned (thegreenleaf.com)

---

## Commands Reference

### Content Pipeline
```bash
# Full automated pipeline
python weekly_content_pipeline.py

# With options
python weekly_content_pipeline.py --keyword "cannabis aeration tips"
python weekly_content_pipeline.py --count 3 --no-qa
python weekly_content_pipeline.py --no-publish
python weekly_content_pipeline.py --dry-run
python weekly_content_pipeline.py --ci  # GitHub Actions mode
```

### Individual Scripts
```bash
# Keyword research
python keyword_research.py
python keyword_research.py --count 5 --season spring

# QA analysis
python article_qa.py --test drafts/my-article.md
python article_qa.py --analyze --days 30

# Cost reports
python cost_tracker.py --report

# Auto-publish
python auto_publish.py
python auto_publish.py --dry-run

# Content freshness check
python freshness_tracker.py
```

### Next.js Site
```bash
cd site
npm run dev       # Development (http://localhost:3001)
npm run build     # Production build
npm run lint      # Lint check
```

---

## Development History

### Phase 1 (November 2025) - Foundation
- Python content generator with Claude Sonnet 4
- Next.js site with Tailwind CSS
- OpenAI DALL-E image generation (later replaced)
- Vercel deployment
- Legal pages (privacy, terms, affiliate disclosure)
- Technical SEO (sitemap, structured data, Open Graph)

### Phase 2 (December 2025) - Enhancement
- Migrated images from DALL-E to Runware AI
- Added YouTube video integration (search, transcripts, embedding)
- Built QA evaluation system with auto-refinement
- Implemented affiliate linking with product database
- Added internal cross-article linking
- Created keyword research pipeline with Google Trends
- Set up GitHub Actions automation (Mon/Wed schedule)
- Added content calendar and freshness tracking
- Built search functionality
- Added videos page and topics pages
- Integrated PostHog analytics
- Implemented cost tracking

### Phase 3 (January 2026) - Scale
- 66 published articles with 158 images
- 132+ embedded YouTube videos
- Fully automated pipeline running 2x/week
- GSC integration for SEO monitoring

---

## Owner & Maintenance

**Owner:** Jacob Taylor
**Project Location:** `/Users/jacobtaylor/Desktop/The Green Leaf 2025/cannabiscare-content-engine`

**Automated:**
- Content generation: Monday & Wednesday (GitHub Actions)
- Deployment: Auto on push to main (Vercel)

**Manual:**
- Review QA logs and adjust thresholds as needed
- Monitor GSC performance and content freshness
- Update product database as new affiliate items become available
