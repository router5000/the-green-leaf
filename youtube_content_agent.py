#!/usr/bin/env python3
"""
YouTube Content Agent for The Green Leaf Content Engine

This agent inverts the typical content flow:
- CURRENT: Keyword → Article → Find supporting videos
- AGENT:   Popular video → Transcript → Article (video already embedded)

Usage:
    python youtube_content_agent.py                    # Find and process top video
    python youtube_content_agent.py --count 3         # Process top 3 videos
    python youtube_content_agent.py --channel "Cannabis Nut"  # From specific channel
    python youtube_content_agent.py --dry-run         # Preview without generating
    python youtube_content_agent.py --run-pipeline    # Full pipeline (images, affiliates, QA)
"""

import os
import json
import re
import argparse
import math
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from anthropic import Anthropic
import requests

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")

# SupaData fallback for transcripts when YouTube API fails
USE_SUPADATA_FALLBACK = True

# Paths (adjust to match your project structure)
DRAFTS_DIR = Path("drafts")
POSTS_DIR = Path("site/content/posts")
IMAGES_DIR = Path("site/public/images/articles")
CACHE_DIR = Path(".cache/youtube_agent")

# Discovery settings
SEARCH_QUERIES = [
    "cannabis tips",
    "cannabis tutorial",
    "grass care guide",
    "cannabis maintenance",
    "how to cannabis",
    "cannabis mistakes",
    "cannabis fertilizer",
    "cannabis aeration",
    "cannabis mowing tips",
    "weed control cannabis",
    "cannabis watering guide",
    "cannabis spring",
    "cannabis fall",
    "overseeding cannabis",
    "cannabis dethatching",
]

# Trusted channels (optional - boost their scores)
TRUSTED_CHANNELS = [
    "Cannabis Nut",
    "Ryan Knorr Cannabis",
    "How To with Doc",
    "Pest and Cannabis Ginja",
    "The Cannabis Nut",
    "Cannabiscology",
]

# Video filtering criteria
MIN_VIEWS = 10_000
MIN_DURATION_SECONDS = 180  # 3 minutes
MAX_DURATION_SECONDS = 1800  # 30 minutes
MAX_AGE_DAYS = 365  # Videos from last year
REQUIRED_TRANSCRIPT = True


# =============================================================================
# YOUTUBE DISCOVERY
# =============================================================================

class YouTubeDiscovery:
    """Discovers high-value cannabis videos for content generation."""

    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def search_trending_videos(
        self,
        max_results: int = 50,
        channel_filter: Optional[str] = None
    ) -> list[dict]:
        """
        Search for high-performing cannabis videos.

        Returns list of video candidates sorted by value score.
        """
        all_videos = []

        # Search across multiple queries for diversity
        queries = SEARCH_QUERIES if not channel_filter else [f"{channel_filter} cannabis"]

        for query in queries[:5]:  # Limit to avoid quota burn
            try:
                request = self.youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    order="viewCount",  # Sort by popularity
                    publishedAfter=(datetime.now() - timedelta(days=MAX_AGE_DAYS)).isoformat() + "Z",
                    maxResults=10,
                    videoDuration="medium",  # 4-20 minutes
                    relevanceLanguage="en",
                )
                response = request.execute()

                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    if not any(v["id"] == video_id for v in all_videos):
                        all_videos.append({
                            "id": video_id,
                            "title": item["snippet"]["title"],
                            "channel": item["snippet"]["channelTitle"],
                            "channel_id": item["snippet"]["channelId"],
                            "published_at": item["snippet"]["publishedAt"],
                            "description": item["snippet"].get("description", ""),
                            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                        })
            except Exception as e:
                print(f"Search error for '{query}': {e}")
                continue

        # Enrich with statistics
        enriched = self._enrich_with_stats(all_videos)

        # Score and sort
        scored = self._score_videos(enriched)

        return sorted(scored, key=lambda x: x["value_score"], reverse=True)[:max_results]

    def _enrich_with_stats(self, videos: list[dict]) -> list[dict]:
        """Add view counts, likes, duration from YouTube API."""
        if not videos:
            return videos

        video_ids = [v["id"] for v in videos]

        # YouTube API has a 50 ID limit per request - batch accordingly
        stats_map = {}
        batch_size = 50
        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i + batch_size]
            request = self.youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(batch_ids)
            )
            response = request.execute()

            for item in response.get("items", []):
                duration_str = item["contentDetails"]["duration"]
                stats_map[item["id"]] = {
                    "views": int(item["statistics"].get("viewCount", 0)),
                    "likes": int(item["statistics"].get("likeCount", 0)),
                    "comments": int(item["statistics"].get("commentCount", 0)),
                    "duration_seconds": self._parse_duration(duration_str),
                }

        for video in videos:
            stats = stats_map.get(video["id"], {})
            video.update(stats)

        return videos

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    def _score_videos(self, videos: list[dict]) -> list[dict]:
        """
        Calculate value score based on multiple factors.

        Score components:
        - View count (log scaled)
        - Engagement rate (likes/views)
        - Recency bonus
        - Trusted channel bonus
        - Duration sweet spot (8-15 min ideal)
        """
        for video in videos:
            views = video.get("views", 0)
            likes = video.get("likes", 0)
            duration = video.get("duration_seconds", 0)
            channel = video.get("channel", "")
            published = video.get("published_at", "")

            # Skip if doesn't meet minimums
            if views < MIN_VIEWS:
                video["value_score"] = 0
                video["skip_reason"] = "Below minimum views"
                continue

            if duration < MIN_DURATION_SECONDS or duration > MAX_DURATION_SECONDS:
                video["value_score"] = 0
                video["skip_reason"] = "Duration out of range"
                continue

            # Base score from views (log scale, 10k views = 4, 100k = 5, 1M = 6)
            view_score = math.log10(views) if views > 0 else 0

            # Engagement rate bonus (0-2 points)
            engagement_rate = (likes / views * 100) if views > 0 else 0
            engagement_score = min(engagement_rate / 2, 2)

            # Recency bonus (up to 1.5 points for videos < 30 days old)
            try:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
                recency_score = max(0, 1.5 - (days_old / 60))
            except:
                recency_score = 0

            # Trusted channel bonus (1 point)
            channel_score = 1 if any(tc.lower() in channel.lower() for tc in TRUSTED_CHANNELS) else 0

            # Duration sweet spot (8-15 minutes ideal, up to 0.5 points)
            ideal_duration = 600  # 10 minutes
            duration_diff = abs(duration - ideal_duration)
            duration_score = max(0, 0.5 - (duration_diff / 1200))

            # Total score
            video["value_score"] = round(
                view_score + engagement_score + recency_score + channel_score + duration_score,
                2
            )
            video["score_breakdown"] = {
                "views": round(view_score, 2),
                "engagement": round(engagement_score, 2),
                "recency": round(recency_score, 2),
                "channel": channel_score,
                "duration": round(duration_score, 2),
            }

        return videos

    def get_transcript(self, video_id: str) -> tuple[Optional[str], str]:
        """
        Extract transcript from YouTube video.

        Returns: (transcript_text, source) where source is 'youtube_api' or 'supadata'
        """
        # Try YouTube API first (free)
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            full_text = " ".join([entry.text for entry in transcript_list])
            return full_text, "youtube_api"
        except Exception as e:
            print(f"   YouTube transcript unavailable: {e}")

        # Fallback to SupaData
        if USE_SUPADATA_FALLBACK:
            print(f"   Trying SupaData fallback...")
            transcript = self._get_transcript_supadata(video_id)
            if transcript:
                print(f"   ✓ Got transcript via SupaData")
                return transcript, "supadata"

        return None, ""

    def _get_transcript_supadata(self, video_id: str) -> Optional[str]:
        """Fallback transcript via SupaData API."""
        if not SUPADATA_API_KEY:
            print(f"   ⚠️  SUPADATA_API_KEY not set")
            return None

        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            response = requests.get(
                "https://api.supadata.ai/v1/transcript",
                headers={"x-api-key": SUPADATA_API_KEY},
                params={"url": video_url, "text": "true", "lang": "en"},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("content")
            else:
                print(f"   SupaData error: {response.status_code} - {response.text[:100]}")
                return None
        except Exception as e:
            print(f"   SupaData exception: {e}")
            return None

    def check_transcript_available(self, video_id: str) -> bool:
        """Quick check if transcript exists."""
        try:
            # youtube-transcript-api v1.x requires instantiation
            api = YouTubeTranscriptApi()
            api.list(video_id)
            return True
        except:
            return False


# =============================================================================
# DUPLICATE DETECTION
# =============================================================================

class DuplicateDetector:
    """Prevents generating articles for already-covered topics."""

    def __init__(self):
        self.existing_articles = self._load_existing_articles()
        self.processed_videos = self._load_processed_videos()

    def _load_existing_articles(self) -> list[dict]:
        """Load metadata from existing articles."""
        articles = []

        for posts_dir in [POSTS_DIR, DRAFTS_DIR]:
            if not posts_dir.exists():
                continue
            for md_file in posts_dir.glob("*.md"):
                try:
                    content = md_file.read_text()
                    frontmatter = self._extract_frontmatter(content)
                    articles.append({
                        "slug": md_file.stem,
                        "title": frontmatter.get("title", ""),
                        "keyword": frontmatter.get("keyword", ""),
                        "youtube_ids": self._extract_youtube_ids(frontmatter),
                    })
                except Exception as e:
                    print(f"Error loading {md_file}: {e}")

        return articles

    def _extract_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown."""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except:
                pass
        return {}

    def _extract_youtube_ids(self, frontmatter: dict) -> list[str]:
        """Get YouTube video IDs from frontmatter."""
        youtube = frontmatter.get("youtube", [])
        if isinstance(youtube, list):
            return [v.get("id") for v in youtube if isinstance(v, dict) and v.get("id")]
        return []

    def _load_processed_videos(self) -> set[str]:
        """Load list of already-processed video IDs."""
        cache_file = CACHE_DIR / "processed_videos.json"
        if cache_file.exists():
            try:
                return set(json.loads(cache_file.read_text()))
            except:
                pass
        return set()

    def _save_processed_video(self, video_id: str):
        """Mark video as processed."""
        self.processed_videos.add(video_id)
        cache_file = CACHE_DIR / "processed_videos.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(list(self.processed_videos)))

    def is_duplicate(self, video: dict, transcript: str) -> tuple[bool, Optional[str]]:
        """
        Check if video/topic has already been covered.

        Returns: (is_duplicate, reason)
        """
        video_id = video["id"]
        video_title = video["title"].lower()

        # Check 1: Video ID already used
        if video_id in self.processed_videos:
            return True, "Video already processed"

        for article in self.existing_articles:
            if video_id in article.get("youtube_ids", []):
                return True, f"Video used in article: {article['slug']}"

        # Check 2: Very similar title (basic check)
        for article in self.existing_articles:
            existing_title = article.get("title", "").lower()
            if self._titles_similar(video_title, existing_title):
                return True, f"Similar title exists: {article['slug']}"

        return False, None

    def _titles_similar(self, title1: str, title2: str) -> bool:
        """Basic title similarity check."""
        # Normalize
        def normalize(t):
            t = re.sub(r'[^\w\s]', '', t.lower())
            stopwords = {'the', 'a', 'an', 'to', 'how', 'for', 'your', 'my', 'in', 'on', 'and', 'or', 'of'}
            return set(t.split()) - stopwords

        words1 = normalize(title1)
        words2 = normalize(title2)

        if not words1 or not words2:
            return False

        # Jaccard similarity > 0.6 = likely duplicate
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        similarity = intersection / union if union > 0 else 0

        return similarity > 0.6

    def mark_processed(self, video_id: str):
        """Mark video as processed after successful article generation."""
        self._save_processed_video(video_id)


# =============================================================================
# ARTICLE GENERATOR
# =============================================================================

class ArticleGenerator:
    """Generates articles from YouTube video transcripts."""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def generate_from_transcript(
        self,
        video: dict,
        transcript: str
    ) -> dict:
        """
        Transform video transcript into original article.

        Returns article metadata and content.
        """
        prompt = self._build_prompt(video, transcript)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Parse the response
        return self._parse_response(content, video)

    def _build_prompt(self, video: dict, transcript: str) -> str:
        """Build the article generation prompt."""
        # Truncate transcript if too long
        max_transcript_len = 12000
        truncated_transcript = transcript[:max_transcript_len]
        if len(transcript) > max_transcript_len:
            truncated_transcript += "\n\n[Transcript truncated...]"

        return f"""You are a cannabis content expert. Transform this YouTube video transcript into an original, SEO-optimized article.

## Source Video
- Title: {video['title']}
- Channel: {video['channel']}
- Views: {video.get('views', 'N/A'):,}

## Transcript
{truncated_transcript}

## Requirements

### Content Guidelines
1. Write an ORIGINAL article inspired by the video - do NOT just transcribe or summarize
2. Extract key insights, tips, and techniques from the transcript
3. Reorganize into logical written structure (may differ from video flow)
4. Add context, explanations, and practical advice
5. Target 600-750 words
6. Write for homeowners, not professionals

### Structure
1. **Title**: SEO-optimized, 50-60 characters, includes primary keyword
2. **Meta Description**: 150-160 characters, compelling and descriptive
3. **Primary Keyword**: Extract the main topic as a keyword phrase
4. **Quick Answer**: 2-3 sentence direct answer for featured snippets
5. **Key Takeaways**: 3-5 bullet points
6. **Body**: 3-4 H2 sections with practical, actionable content
7. **Sources**: Credit the video and add 2-3 authoritative cannabis sources

### Tone
- Helpful and encouraging
- Practical and actionable
- Accessible to beginners
- Confident but not preachy

## Output Format
Return as JSON with this structure:
```json
{{
    "title": "Article Title Here",
    "meta_description": "Meta description here",
    "keyword": "primary keyword phrase",
    "quick_answer": "Quick answer text",
    "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
    "content": "Full markdown article body (H2 sections, paragraphs)",
    "sources": [
        {{"name": "Source Name", "url": "https://..."}}
    ],
    "suggested_slug": "suggested-url-slug"
}}
```

Generate the article now:"""

    def _parse_response(self, response: str, video: dict) -> dict:
        """Parse Claude's response into structured article data."""
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                # Try to parse the whole response as JSON
                data = json.loads(response)
        else:
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                raise ValueError("Could not parse article JSON from response")

        # Add video metadata
        data["source_video"] = {
            "id": video["id"],
            "title": video["title"],
            "channel": video["channel"],
            "views": video.get("views"),
            "url": f"https://www.youtube.com/watch?v={video['id']}",
        }

        return data


# =============================================================================
# PIPELINE INTEGRATION
# =============================================================================

class PipelineIntegration:
    """Integrates with existing content pipeline components."""

    def __init__(self):
        self.drafts_dir = DRAFTS_DIR
        self.drafts_dir.mkdir(exist_ok=True)

    def create_draft(self, article: dict, video: dict) -> Path:
        """
        Create draft markdown file with frontmatter.

        This draft can then be processed by existing pipeline:
        - affiliate_linker.py
        - article_qa.py
        - Image generation
        """
        slug = article.get("suggested_slug", self._generate_slug(article["title"]))

        # Build frontmatter
        frontmatter = {
            "title": article["title"],
            "slug": slug,
            "meta_description": article["meta_description"],
            "keyword": article["keyword"],
            "featured_image": f"/images/articles/{slug}.jpg",
            "featured_image_alt": f"{article['keyword']} - hero image",
            "section_image": f"/images/articles/{slug}-section.jpg",
            "section_image_alt": f"{article['keyword']} - section image",
            "youtube": [{
                "id": video["id"],
                "title": video["title"],
                "channel": video["channel"],
                "position": "hero",
                "insights": {
                    "source_video": True,
                    "views": video.get("views"),
                }
            }],
            "tags": ["cannabis", self._extract_season(article["keyword"])],
            "season": self._extract_season(article["keyword"]),
            "category": self._categorize(article["title"], article["keyword"]),
            "status": "draft",
            "has_affiliate_links": False,
            "affiliate_count": 0,
            "source": "youtube_agent",
            "source_video_id": video["id"],
            "transcript_source": video.get("transcript_source", "youtube_api"),
            "generated_at": datetime.now().isoformat(),
        }

        # Build markdown content
        content = self._build_markdown(article, frontmatter)

        # Write draft file
        draft_path = self.drafts_dir / f"{slug}.md"
        draft_path.write_text(content)

        return draft_path

    def _build_markdown(self, article: dict, frontmatter: dict) -> str:
        """Build complete markdown file with frontmatter."""
        # YAML frontmatter
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Quick answer section
        quick_answer = f"""## Quick Answer

{article['quick_answer']}"""

        # Key takeaways
        takeaways = "\n".join([f"- {t}" for t in article.get("key_takeaways", [])])
        takeaways_section = f"""## Key Takeaways

{takeaways}"""

        # Main content
        body = article.get("content", "")

        # Sources section
        sources = article.get("sources", [])
        source_links = "\n".join([f"- [{s['name']}]({s['url']})" for s in sources])
        sources_section = f"""## Sources

{source_links}"""

        return f"""---
{yaml_str}---

{quick_answer}

{takeaways_section}

{body}

{sources_section}
"""

    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title."""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')[:60]

    def _extract_season(self, keyword: str) -> str:
        """Extract season tag from keyword if present."""
        keyword_lower = keyword.lower()
        for season in ["spring", "summer", "fall", "autumn", "winter"]:
            if season in keyword_lower:
                return season if season != "autumn" else "fall"
        return "seasonal"

    def _categorize(self, title: str, keyword: str) -> str:
        """Assign article category based on title/keyword content."""
        clusters = [
            ("Weed Control", ["weed", "crabgrass", "spurge", "pre-emergent", "herbicide", "kill"]),
            ("Cannabis Problems & Solutions", ["problem", "disease", "fungus", "fungicide", "yellow", "dead spot", "bumpy", "patchy"]),
            ("Equipment & Techniques", ["mow", "trimmer", "mower", "robot mow", "string trimmer", "scalp"]),
            ("Grass Types & Seeding", ["seed", "overseed", "grass type", "germination", "grow grass"]),
            ("Seasonal Care", ["spring", "summer", "fall", "winter", "winterize"]),
            ("Cannabis Health & Maintenance", ["fertiliz", "aerat", "dethatch", "water", "level", "green"]),
        ]
        text = f"{title} {keyword}".lower()
        best_score, best_cat = 0, "Cannabis Health & Maintenance"
        for cat, kws in clusters:
            score = sum(1 for kw in kws if kw in text)
            if score > best_score:
                best_score, best_cat = score, cat
        return best_cat

    def run_existing_pipeline(self, draft_path: Path, run_full: bool = False) -> dict:
        """
        Run existing pipeline components on the draft.

        This calls your existing scripts:
        1. Image generation (Runware)
        2. Affiliate link insertion
        3. QA scoring

        Returns pipeline results.
        """
        results = {
            "draft_path": str(draft_path),
            "images_generated": False,
            "affiliates_added": False,
            "qa_score": None,
        }

        slug = draft_path.stem

        if run_full:
            print(f"\n🔄 Running full pipeline on {slug}...")

            # 1. Generate images
            try:
                from content_generator import generate_article_images
                print(f"   🖼️  Generating images...")
                generate_article_images(slug, draft_path)
                results["images_generated"] = True
                print(f"   ✅ Images generated")
            except ImportError:
                print(f"   ⚠️  Could not import image generator - run manually")
            except Exception as e:
                print(f"   ❌ Image generation failed: {e}")

            # 2. Add affiliate links
            try:
                from affiliate_linker import process_article_for_affiliates
                print(f"   🔗 Adding affiliate links...")
                affiliate_result = process_article_for_affiliates(str(draft_path))
                results["affiliates_added"] = affiliate_result.get("links_added", 0) > 0
                results["affiliate_count"] = affiliate_result.get("links_added", 0)
                print(f"   ✅ Added {results['affiliate_count']} affiliate links")
            except ImportError:
                print(f"   ⚠️  Could not import affiliate linker - run manually")
            except Exception as e:
                print(f"   ❌ Affiliate linking failed: {e}")

            # 3. Run QA
            try:
                from article_qa import evaluate_article_quality
                print(f"   📊 Running QA evaluation...")
                qa_result = evaluate_article_quality(str(draft_path))
                results["qa_score"] = qa_result.get("overall_score")
                results["qa_passed"] = qa_result.get("passed", False)
                print(f"   ✅ QA Score: {results['qa_score']}")
            except ImportError:
                print(f"   ⚠️  Could not import QA module - run manually")
            except Exception as e:
                print(f"   ❌ QA evaluation failed: {e}")
        else:
            print(f"\n📋 Draft created: {draft_path}")
            print(f"   Run these commands to complete processing:")
            print(f"   1. python content_generator.py --generate-images {slug}")
            print(f"   2. python affiliate_linker.py {draft_path}")
            print(f"   3. python article_qa.py {draft_path}")

        return results


# =============================================================================
# MAIN AGENT
# =============================================================================

class YouTubeContentAgent:
    """
    Main agent that orchestrates the YouTube-first content flow.

    Flow:
    1. Discover trending cannabis videos
    2. Filter by quality, transcript availability, duplicates
    3. Generate original article from transcript
    4. Create draft for existing pipeline
    """

    def __init__(self):
        self.discovery = YouTubeDiscovery()
        self.duplicate_detector = DuplicateDetector()
        self.article_generator = ArticleGenerator()
        self.pipeline = PipelineIntegration()

    def run(
        self,
        count: int = 1,
        channel_filter: Optional[str] = None,
        dry_run: bool = False,
        run_pipeline: bool = False
    ) -> list[dict]:
        """
        Run the agent to generate articles from trending videos.

        Args:
            count: Number of articles to generate
            channel_filter: Only consider videos from this channel
            dry_run: Preview videos without generating articles
            run_pipeline: Run full pipeline (images, affiliates, QA) after generation

        Returns:
            List of results for each processed video
        """
        print("🔍 Discovering trending cannabis videos...")

        # Step 1: Find candidate videos
        candidates = self.discovery.search_trending_videos(
            max_results=50,
            channel_filter=channel_filter
        )

        print(f"   Found {len(candidates)} candidate videos")

        # Step 2: Filter and select best videos (no longer pre-filtering by transcript)
        selected = []
        for video in candidates:
            if len(selected) >= count * 3:  # Get 3x candidates for filtering
                break

            if video.get("value_score", 0) < 4:  # Minimum quality threshold
                continue

            # No longer pre-checking transcripts - we'll try YouTube API + SupaData fallback
            selected.append(video)

        if dry_run:
            return self._preview_videos(selected[:count * 2])

        # Step 3: Process selected videos
        results = []
        processed = 0

        for video in selected:
            if processed >= count:
                break

            print(f"\n📹 Processing: {video['title'][:60]}...")
            print(f"   Channel: {video['channel']} | Views: {video.get('views', 0):,} | Score: {video['value_score']}")

            # Get transcript (tries YouTube API first, then SupaData fallback)
            transcript, transcript_source = self.discovery.get_transcript(video["id"])
            if not transcript:
                print(f"   ❌ Failed to get transcript from any source")
                continue

            # Store transcript source in video metadata for frontmatter
            video["transcript_source"] = transcript_source

            # Check for duplicates
            is_dup, reason = self.duplicate_detector.is_duplicate(video, transcript)
            if is_dup:
                print(f"   ⏭️  Skipping (duplicate): {reason}")
                continue

            try:
                # Generate article
                print(f"   ✍️  Generating article...")
                article = self.article_generator.generate_from_transcript(video, transcript)

                # Create draft
                print(f"   📄 Creating draft...")
                draft_path = self.pipeline.create_draft(article, video)

                # Mark as processed
                self.duplicate_detector.mark_processed(video["id"])

                # Run pipeline (or print instructions)
                pipeline_results = self.pipeline.run_existing_pipeline(draft_path, run_full=run_pipeline)

                results.append({
                    "status": "success",
                    "video": video,
                    "article": article,
                    "draft_path": str(draft_path),
                    "pipeline": pipeline_results,
                })

                processed += 1
                print(f"   ✅ Article generated: {article['title']}")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    "status": "error",
                    "video": video,
                    "error": str(e),
                })

        return results

    def _preview_videos(self, videos: list[dict]) -> list[dict]:
        """Preview mode - show video candidates without processing."""
        print(f"\n{'='*60}")
        print("DRY RUN - Preview of candidate videos")
        print(f"{'='*60}\n")

        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   Channel: {video['channel']}")
            print(f"   Views: {video.get('views', 0):,} | Score: {video['value_score']}")
            if video.get('score_breakdown'):
                breakdown = video['score_breakdown']
                print(f"   Breakdown: views={breakdown['views']}, engagement={breakdown['engagement']}, "
                      f"recency={breakdown['recency']}, channel={breakdown['channel']}")
            print(f"   URL: https://youtube.com/watch?v={video['id']}")
            print()

        return [{"status": "preview", "video": v} for v in videos]


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Content Agent - Generate articles from trending cannabis videos"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=1,
        help="Number of articles to generate (default: 1)"
    )
    parser.add_argument(
        "--channel",
        type=str,
        help="Only consider videos from this channel"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview candidate videos without generating articles"
    )
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        help="Run full pipeline (images, affiliates, QA) after generation"
    )
    parser.add_argument(
        "--min-views",
        type=int,
        default=10000,
        help="Minimum view count for videos (default: 10,000)"
    )

    args = parser.parse_args()

    # Validate API keys
    if not YOUTUBE_API_KEY:
        print("❌ Error: YOUTUBE_API_KEY environment variable not set")
        return
    if not ANTHROPIC_API_KEY and not args.dry_run:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Run agent
    agent = YouTubeContentAgent()
    results = agent.run(
        count=args.count,
        channel_filter=args.channel,
        dry_run=args.dry_run,
        run_pipeline=args.run_pipeline
    )

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    success = [r for r in results if r.get("status") == "success"]
    errors = [r for r in results if r.get("status") == "error"]
    previews = [r for r in results if r.get("status") == "preview"]

    if previews:
        print(f"📋 Previewed: {len(previews)} videos")
    else:
        print(f"✅ Generated: {len(success)} articles")
        print(f"❌ Errors: {len(errors)}")

        if success:
            print(f"\nDrafts created:")
            for r in success:
                print(f"  - {r['draft_path']}")


if __name__ == "__main__":
    main()
