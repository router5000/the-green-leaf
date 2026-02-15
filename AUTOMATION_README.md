# Cannabis Automated Content Pipeline

Fully automated content generation system that:
1. **Researches** trending cannabis keywords via Google Trends
2. **Generates** SEO-optimized articles with AI images, YouTube videos, and affiliate links
3. **Evaluates** content quality with multi-dimensional QA scoring
4. **Links** articles internally and inserts relevant affiliate products
5. **Publishes** automatically via Git push → Vercel deployment

**Live Site:** https://thegreenleaf.com
**GitHub:** https://github.com/JakeTaylorDesign/cannabiscare-center

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (auto-select keyword)
python weekly_content_pipeline.py

# Generate 3 articles
python weekly_content_pipeline.py --count 3

# Use a specific keyword
python weekly_content_pipeline.py --keyword "spring cannabis fertilizer schedule"

# Dry run (see what would happen)
python weekly_content_pipeline.py --dry-run
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions (Scheduled Cron)                │
│             Monday & Wednesday @ 8am UTC                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   KEYWORD RESEARCH                          │
│  keyword_research.py + content_calendar.py                  │
│  ├─ Google Trends API (trending topics)                     │
│  ├─ Keywords Everywhere API (search volume, optional)       │
│  ├─ Seasonal relevance scoring                              │
│  ├─ Content calendar topic balancing                        │
│  └─ Filter already-published topics                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONTENT GENERATION                         │
│  content_generator.py                                       │
│  ├─ Claude Sonnet 4 (article writing)                       │
│  ├─ Runware API (photorealistic images, 16:9 + 4:3)        │
│  ├─ YouTube API (video search + transcript extraction)      │
│  ├─ Affiliate link insertion (Amazon Associates)            │
│  ├─ Internal linking (cross-article SEO links)              │
│  └─ QA evaluation & auto-refinement                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    AUTO-PUBLISH                             │
│  auto_publish.py                                            │
│  ├─ Git add/commit/push                                     │
│  └─ Vercel auto-deploys from main                           │
└─────────────────────────────────────────────────────────────┘
```

## Files

### Content Generation
| File | Purpose |
|------|---------|
| `content_generator.py` | Main article generation (Claude + Runware images) |
| `youtube_content_agent.py` | Video-first article generation from YouTube trending |
| `weekly_content_pipeline.py` | Full pipeline orchestration |
| `auto_publish.py` | Git commit/push automation |

### Content Enhancement
| File | Purpose |
|------|---------|
| `affiliate_linker.py` | Amazon affiliate link insertion (34 products, 14 categories) |
| `internal_linker.py` | Auto-links related articles for SEO |
| `article_qa.py` | Multi-dimensional quality assurance scoring |
| `youtube_search.py` | Video discovery, transcript extraction, caching |
| `regenerate_article.py` | Refresh/update existing articles |
| `regenerate_images.py` | Image regeneration utilities |

### Research & Planning
| File | Purpose |
|------|---------|
| `keyword_research.py` | Google Trends + keyword scoring |
| `content_calendar.py` | Topic balancing & distribution |
| `freshness_tracker.py` | Stale article detection |

### Monitoring & Tracking
| File | Purpose |
|------|---------|
| `cost_tracker.py` | API cost tracking per article |
| `gsc_tracker.py` | Google Search Console integration |
| `rate_limiter.py` | API rate limiting |

### Configuration
| File | Purpose |
|------|---------|
| `.github/workflows/weekly-content.yml` | GitHub Actions automation |
| `products/cannabis_products.json` | Affiliate product database |
| `requirements.txt` | Python dependencies |

## GitHub Actions Setup

### 1. Add Repository Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

**Required secrets:**
- `ANTHROPIC_API_KEY` - Your Claude API key
- `RUNWARE_API_KEY` - Runware image generation key
- `YOUTUBE_API_KEY` - Google/YouTube API key
- `AMAZON_AFFILIATE_TAG` - Your Amazon affiliate tag

**Optional secrets:**
- `SUPADATA_API_KEY` - YouTube transcript fallback
- `KEYWORDS_EVERYWHERE_API_KEY` - For search volume data
- `NOTIFICATION_WEBHOOK_URL` - Discord/Slack webhook for failure notifications

### 2. Enable GitHub Actions

The workflow file at `.github/workflows/weekly-content.yml` will:
- Run automatically Monday and Wednesday at 8am UTC (3am EST)
- Can be triggered manually from the Actions tab
- Supports custom inputs (keyword, count, season, skip_qa, dry_run)

### 3. Manual Trigger

1. Go to Actions tab in your repo
2. Select "Weekly Content Generation"
3. Click "Run workflow"
4. Optionally specify keyword, count, season

## Keyword Research

### How It Works

1. **Topic Bank**: 75+ curated cannabis topics organized by season
2. **Google Trends**: Gets relative interest scores (0-100)
3. **Seasonal Relevance**: Prioritizes current + upcoming season
4. **Duplicate Check**: Filters out already-published topics
5. **Scoring**: Combines all factors to rank keywords

### Scoring Formula

```
Score = (Trends × 0.30) + (Volume × 0.30) + (Seasonal × 0.30) + (Novelty × 0.10)
```

### Adding Custom Keywords

Edit `CANNABIS_TOPICS` in `keyword_research.py`:

```python
CANNABIS_TOPICS = {
    "spring": [
        "your new keyword here",
        # ...
    ],
    # ...
}
```

### Keywords Everywhere API (Optional)

For actual search volume data:

1. Get API key from [keywordseverywhere.com](https://keywordseverywhere.com) (~$10)
2. Add to `.env`: `KEYWORDS_EVERYWHERE_API_KEY=your_key`
3. The system will automatically use it

## Commands

```bash
# Full pipeline (research → generate → publish)
python weekly_content_pipeline.py

# Just keyword research
python keyword_research.py
python keyword_research.py --count 5  # Top 5 keywords
python keyword_research.py --season spring  # Force season
python keyword_research.py --trending  # Show trending topics

# Just auto-publish
python auto_publish.py
python auto_publish.py --dry-run  # See what would happen
python auto_publish.py --status  # Just show git status

# Pipeline with options
python weekly_content_pipeline.py --keyword "cannabis aeration tips"
python weekly_content_pipeline.py --count 3 --no-qa
python weekly_content_pipeline.py --no-publish  # Generate but don't push
python weekly_content_pipeline.py --dry-run  # Preview only
```

## Cost Estimates

| Component | Cost per Article |
|-----------|-----------------|
| Content generation (Claude Sonnet 4) | ~$0.02-0.05 |
| QA evaluation (Claude) | ~$0.02-0.03 |
| Images (Runware, 2 per article) | ~$0.04-0.06 |
| Video evaluation (Claude) | ~$0.01-0.02 |
| Affiliate link detection (Claude) | ~$0.01 |
| Keyword research (Trends) | Free |
| YouTube API | Free |
| GitHub Actions | Free (2,000 min/month) |
| **Total per article** | **~$0.10-0.15** |

**2 articles/week (current schedule):** ~$0.80-1.20/month
**Higher volume (3 articles/week):** ~$1.50-2.00/month

## Monitoring

### Logs

Pipeline runs are logged to `.logs/pipeline_YYYYMM.jsonl`:

```json
{
  "timestamp": "2024-12-20T10:30:00",
  "status": "success",
  "keyword": "spring cannabis tips",
  "details": {
    "generated": ["spring cannabis tips"],
    "failed": []
  }
}
```

### Notifications (Optional)

Set `NOTIFICATION_WEBHOOK_URL` to receive Discord/Slack notifications:

```
# Discord webhook
https://discord.com/api/webhooks/xxx/yyy

# Slack webhook
https://hooks.slack.com/services/xxx/yyy/zzz
```

## Troubleshooting

### "No suitable keywords found"

All topic bank keywords have been published. Solutions:
1. Add more topics to `CANNABIS_TOPICS`
2. Use `--keyword` to specify a custom keyword
3. Run `python keyword_research.py --trending` to discover new topics

### "Content generation failed"

Check:
1. API keys are valid and have credits
2. Network connectivity
3. Run with `--no-qa` to skip QA step

### "Push failed"

Check:
1. Git is configured with proper credentials
2. You have write access to the repo
3. Branch protection rules allow pushes

### GitHub Actions not running

1. Check Actions tab for errors
2. Verify secrets are set correctly
3. Check workflow file syntax at [actionlint](https://rhysd.github.io/actionlint/)

## Customization

### Change Schedule

Edit `.github/workflows/weekly-content.yml`:

```yaml
schedule:
  # Every day at 8am UTC
  - cron: '0 8 * * *'
  
  # Monday and Thursday at 8am UTC
  - cron: '0 8 * * 1,4'
  
  # Every 6 hours
  - cron: '0 */6 * * *'
```

### Add More Seasons/Topics

The topic bank is designed for US-based cannabis. For other regions:
1. Adjust season dates in `get_current_season()`
2. Add region-specific topics to `CANNABIS_TOPICS`

### Different Notification Service

Modify `send_notification()` in `weekly_content_pipeline.py` for other services.

## Current Stats

- **Published articles:** 66
- **Generated images:** 158
- **Affiliate products database:** 34 products across 14 categories
- **Embedded YouTube videos:** 132+
- **Schedule:** Monday & Wednesday at 8am UTC

---

**Last Updated:** January 2026
