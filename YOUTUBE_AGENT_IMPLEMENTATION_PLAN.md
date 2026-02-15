# YouTube Content Agent - Implementation Plan

## Overview

This agent provides an **alternative content workflow** that complements the existing keyword-first process:

| Current Process | Agent Process |
|-----------------|---------------|
| Keyword → Article → Find Videos | Popular Video → Transcript → Article |
| Content drives video selection | Video drives content creation |
| Videos added as supplementary | Video is the primary source |

**Important:** The existing `content_generator.py` workflow remains unchanged. This is an additional tool.

---

## Code Review & Issues to Fix

### Typos in Provided Code

| Location | Issue | Fix |
|----------|-------|-----|
| Line ~35 | `MIN_DURATNDS = 180` | `MIN_DURATION_SECONDS = 180` |
| Line ~226 | `def init__(self):` | `def __init__(self):` |
| Line ~297 | `print(f"   Channel: {video['channel']}...` (malformed) | Fix indentation/spacing |
| Line ~309 | `# Mark as process` (incomplete) | Complete the line |
| Line ~357 | `args.nel` | `args.channel` |

### Missing Imports

```python
import yaml  # Needed in PipelineIntegration._build_markdown()
```

### Logic Issues

1. **`_titles_similar()`** - Basic word overlap may produce false positives for generic titles
2. **`run_existing_pipeline()`** - Currently just prints instructions; needs actual integration
3. **Duration filter** - Uses `videoDuration="medium"` but also manually filters; redundant

---

## Implementation Tasks

### Phase 1: Core Agent (File: `youtube_content_agent.py`)

#### Task 1.1: Create Base File with Fixed Code
- Fix all typos listed above
- Add missing imports (`yaml`, `load_dotenv`)
- Ensure proper class initialization

#### Task 1.2: YouTubeDiscovery Class
- [x] Search trending videos via YouTube API
- [x] Enrich with statistics (views, likes, duration)
- [x] Score videos by value (views, engagement, recency, channel trust)
- [x] Transcript extraction with `youtube-transcript-api`
- Add: Rate limiting awareness for YouTube API quota

#### Task 1.3: DuplicateDetector Class
- [x] Load existing articles from `drafts/` and `site/content/posts/`
- [x] Track processed video IDs in cache
- [x] Basic title similarity check
- Add: Optional Claude-based semantic similarity for better detection

#### Task 1.4: ArticleGenerator Class
- [x] Claude Sonnet integration for transcript → article transformation
- [x] JSON response parsing
- Improve: Add retry logic for API failures
- Improve: Validate JSON structure before returning

#### Task 1.5: PipelineIntegration Class
- [x] Create draft markdown with frontmatter
- Fix: `_build_markdown()` needs YAML import
- Add: Actual integration with existing pipeline components

### Phase 2: Pipeline Integration

#### Task 2.1: Image Generation Integration
Create function to call existing image generation from `content_generator.py`:

```python
def generate_images_for_draft(slug: str) -> bool:
    """
    Generate hero and section images for a draft article.
    Reuses existing Runware integration from content_generator.py
    """
    # Import and call existing image generation functions
    from content_generator import generate_images_for_article
    return generate_images_for_article(slug)
```

#### Task 2.2: Affiliate Links Integration
Call existing `affiliate_linker.py`:

```python
def add_affiliates_to_draft(draft_path: Path) -> dict:
    """Process draft through affiliate linker."""
    from affiliate_linker import process_article_for_affiliates
    return process_article_for_affiliates(str(draft_path))
```

#### Task 2.3: QA Integration
Call existing `article_qa.py`:

```python
def run_qa_on_draft(draft_path: Path) -> dict:
    """Run QA pipeline on draft."""
    from article_qa import quality_assurance_pipeline
    return quality_assurance_pipeline(str(draft_path))
```

### Phase 3: Enhanced Features

#### Task 3.1: Better Duplicate Detection
- Add Claude-based semantic comparison for edge cases
- Consider video content similarity, not just titles

#### Task 3.2: Transcript Insights Extraction
Add richer video insights to frontmatter:

```python
insights = {
    "best_quote": "...",      # Key quote from transcript
    "key_points": [...],       # 3-5 main takeaways
    "pro_tips": [...],         # Actionable advice
    "timestamps": [...]        # Key moments with time codes
}
```

#### Task 3.3: Multi-Video Articles
Support generating articles that synthesize multiple related videos:

```python
def generate_from_multiple_transcripts(videos: list[dict]) -> dict:
    """Combine insights from multiple videos into comprehensive article."""
```

### Phase 4: CLI & Automation

#### Task 4.1: Complete CLI
- [x] `--count` flag for batch processing
- [x] `--channel` flag for channel-specific videos
- [x] `--dry-run` flag for preview mode
- Add: `--min-views` flag to override default
- Add: `--run-pipeline` flag to auto-process through full pipeline

#### Task 4.2: Weekly Integration
Add option to `weekly_content_pipeline.py`:

```python
def weekly_pipeline(mode: str = "keyword"):
    """
    mode: "keyword" (existing) or "youtube" (new agent)
    """
```

---

## File Structure After Implementation

```
cannabiscare-content-engine/
├── content_generator.py          # UNCHANGED - keyword-first process
├── youtube_content_agent.py      # NEW - video-first process
├── youtube_search.py             # Existing module (reused)
├── affiliate_linker.py           # UNCHANGED (called by agent)
├── article_qa.py                 # UNCHANGED (called by agent)
├── weekly_content_pipeline.py    # Updated to support both modes
└── .cache/
    └── youtube_agent/
        └── processed_videos.json # Track processed video IDs
```

---

## Usage Examples

```bash
# Preview top candidate videos (no article generation)
python youtube_content_agent.py --dry-run

# Generate 1 article from top trending video
python youtube_content_agent.py

# Generate 3 articles
python youtube_content_agent.py --count 3

# Only consider videos from specific channel
python youtube_content_agent.py --channel "Cannabis Nut"

# Full pipeline (generate + images + affiliates + QA)
python youtube_content_agent.py --run-pipeline
```

---

## Frontmatter Differences

### Existing Process (keyword-first)
```yaml
youtube:
  - id: "abc123"
    position: "hero"
    insights:
      best_quote: "..."
source: "keyword_generated"  # or not present
```

### Agent Process (video-first)
```yaml
youtube:
  - id: "abc123"
    position: "hero"
    insights:
      source_video: true     # Marks this as the source video
      views: 150000
      best_quote: "..."
source: "youtube_agent"
source_video_id: "abc123"    # Quick reference to primary source
```

---

## Cost Estimates

| Component | Cost per Article |
|-----------|------------------|
| YouTube API | Free (within quota) |
| Claude (transcript → article) | ~$0.03-0.05 |
| Claude (video evaluation) | ~$0.01 |
| Runware (2 images) | ~$0.04 |
| **Total** | **~$0.08-0.10** |

Slightly lower than keyword-first process since we skip keyword research and video search (video is already selected).

---

## Implementation Order

1. **Create `youtube_content_agent.py`** with all fixes applied
2. **Test YouTubeDiscovery** class in isolation
3. **Test DuplicateDetector** with existing articles
4. **Test ArticleGenerator** with sample transcript
5. **Wire up PipelineIntegration** to existing scripts
6. **End-to-end test** with `--dry-run` then full run
7. **Update documentation** (README, PROJECT_OVERVIEW)
8. **Optional:** Add to weekly pipeline

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| YouTube API quota exhaustion | Implement caching, limit searches per run |
| Transcript unavailable | Already handled with `check_transcript_available()` |
| Duplicate content | Multi-layer detection (video ID, title similarity, semantic) |
| Low-quality videos | Value scoring system filters by views, engagement |
| API failures | Add retry logic with exponential backoff |

---

## Success Criteria

- [ ] Agent runs without errors
- [ ] Generates valid markdown with proper frontmatter
- [ ] Integrates cleanly with existing pipeline (images, affiliates, QA)
- [ ] No duplicate articles generated
- [ ] Output quality matches keyword-first process
