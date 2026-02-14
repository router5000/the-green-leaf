"""
YouTube Search Module for Lawncare Content Engine
Searches and evaluates YouTube videos for article relevance.

Usage:
    from youtube_search import find_videos_for_article

    videos = find_videos_for_article(
        keyword="best time to fertilize lawn",
        article_title="When Is the Best Time to Fertilize Your Lawn?",
        article_summary="Guide covering seasonal fertilization timing..."
    )
"""

import os
import json
import hashlib
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from anthropic import Anthropic
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from rate_limiter import wait_for_youtube, wait_for_claude

load_dotenv()

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")

# Curated lawn care channels (optional - for higher quality results)
# Add channel IDs of trusted lawn care YouTubers
CURATED_CHANNELS = [
    # Popular lawn care channels - add more as needed
    # Format: {"id": "channel_id", "name": "Channel Name"}
    {"id": "UCy2V0VrIIYsRHhPsXxZfYEA", "name": "The Lawn Care Nut"},
    {"id": "UCjSrhNjat4GfNLPMqzG3WdQ", "name": "Ryan Knorr Lawn Care"},
    {"id": "UC8fA0sQQz9OLg0b5VjxPmIg", "name": "How To With Doc"},
    {"id": "UC1_xHoP2xkBqRCJJiJ_f5PA", "name": "Lawn Tips"},
    {"id": "UCuPVWCAmwMDYFU6r_HfOjRg", "name": "Silver Cymbal"},
    # Add more trusted channels here
]

# Search settings
MAX_SEARCH_RESULTS = 15  # Number of videos to evaluate
MIN_RELEVANCE_SCORE = 7.0  # Minimum score to include video (out of 10)
MAX_VIDEOS_PER_ARTICLE = 2  # Maximum videos to return

# Cache settings
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "youtube_cache.json"
CACHE_TTL_DAYS = 30  # How long to keep cached results


def _get_cache_key(keyword: str, article_title: str) -> str:
    """Generate a cache key from keyword and article title."""
    combined = f"{keyword.lower().strip()}|{article_title.lower().strip()}"
    return hashlib.md5(combined.encode()).hexdigest()


def _load_cache() -> dict:
    """Load the video cache from disk."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_cache(cache: dict) -> None:
    """Save the video cache to disk."""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def _is_cache_valid(entry: dict) -> bool:
    """Check if a cache entry is still valid."""
    if "cached_at" not in entry:
        return False
    cached_at = datetime.fromisoformat(entry["cached_at"])
    return datetime.now() - cached_at < timedelta(days=CACHE_TTL_DAYS)


def get_cached_videos(keyword: str, article_title: str) -> Optional[list[dict]]:
    """
    Get cached video results if available and valid.

    Returns:
        List of cached videos or None if no valid cache exists
    """
    cache = _load_cache()
    cache_key = _get_cache_key(keyword, article_title)

    if cache_key in cache and _is_cache_valid(cache[cache_key]):
        entry = cache[cache_key]
        print(f"   📦 Using cached results from {entry['cached_at'][:10]}")
        return entry["videos"]

    return None


def cache_videos(keyword: str, article_title: str, videos: list[dict]) -> None:
    """Save video results to cache."""
    cache = _load_cache()
    cache_key = _get_cache_key(keyword, article_title)

    cache[cache_key] = {
        "keyword": keyword,
        "article_title": article_title,
        "cached_at": datetime.now().isoformat(),
        "videos": videos,
    }

    _save_cache(cache)
    print(f"   💾 Cached {len(videos)} videos for future use")


def clear_cache(keyword: str = None, article_title: str = None) -> int:
    """
    Clear cache entries.

    Args:
        keyword: If provided with article_title, clear specific entry
        If neither provided, clear all expired entries

    Returns:
        Number of entries cleared
    """
    cache = _load_cache()
    original_count = len(cache)

    if keyword and article_title:
        # Clear specific entry
        cache_key = _get_cache_key(keyword, article_title)
        if cache_key in cache:
            del cache[cache_key]
            _save_cache(cache)
            return 1
        return 0

    # Clear expired entries
    valid_cache = {k: v for k, v in cache.items() if _is_cache_valid(v)}
    _save_cache(valid_cache)
    return original_count - len(valid_cache)


# Thread lock for rate limiting in parallel searches
_youtube_rate_lock = threading.Lock()


def _rate_limited_search_channel(query: str, channel: dict, max_results: int = 5) -> list[dict]:
    """
    Thread-safe wrapper for channel search with rate limiting.

    Args:
        query: Search query
        channel: Channel dict with "id" and "name"
        max_results: Max videos per channel

    Returns:
        List of video dictionaries
    """
    with _youtube_rate_lock:
        wait_for_youtube()

    # Perform the actual search (outside the lock)
    return _search_channel(query, channel["id"], max_results)


def _search_channels_parallel(query: str, channels: list[dict], max_results_per_channel: int = 5, max_workers: int = 3) -> list[dict]:
    """
    Search multiple channels in parallel with thread-safe rate limiting.

    Args:
        query: Search query
        channels: List of channel dicts
        max_results_per_channel: Max videos per channel
        max_workers: Number of parallel workers (default 3)

    Returns:
        Combined list of videos from all channels
    """
    videos = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_rate_limited_search_channel, query, channel, max_results_per_channel): channel
            for channel in channels
        }

        for future in as_completed(futures):
            channel = futures[future]
            try:
                channel_videos = future.result(timeout=30)
                if channel_videos:
                    videos.extend(channel_videos)
                    print(f"   Found {len(channel_videos)} videos from {channel['name']}")
            except Exception as e:
                print(f"   ⚠️  Error searching {channel['name']}: {e}")

    return videos


def search_youtube(
    query: str,
    max_results: int = MAX_SEARCH_RESULTS,
    use_curated_only: bool = False
) -> list[dict]:
    """
    Search YouTube for videos matching the query.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        use_curated_only: If True, only search within curated channels
        
    Returns:
        List of video dictionaries with id, title, channel, description, etc.
    """
    if not YOUTUBE_API_KEY:
        print("⚠️  YOUTUBE_API_KEY not set in environment")
        return []

    videos = []

    if use_curated_only and CURATED_CHANNELS:
        # Search within each curated channel in parallel
        print(f"   🔍 Searching {len(CURATED_CHANNELS)} curated channels in parallel...")
        videos = _search_channels_parallel(query, CURATED_CHANNELS, max_results_per_channel=5)

        # Enrich all videos with stats in a single batch call
        if videos:
            videos = _enrich_with_stats(videos)
    else:
        # Open search with lawn care context
        search_query = f"{query} lawn care"
        videos = _search_all(search_query, max_results)

    return videos


def _search_all(query: str, max_results: int) -> list[dict]:
    """Search all of YouTube."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "relevance",
        "videoDuration": "medium",  # 4-20 minutes (skip shorts and super long)
        "key": YOUTUBE_API_KEY,
    }
    
    try:
        # Rate limit YouTube API calls
        wait_for_youtube()

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        videos = []
        for item in data.get("items", []):
            videos.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "channel_id": item["snippet"]["channelId"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "published_at": item["snippet"]["publishedAt"],
            })

        # Enrich with video stats
        if videos:
            videos = _enrich_with_stats(videos)
        
        return videos
        
    except requests.RequestException as e:
        print(f"❌ YouTube search error: {e}")
        return []


def _search_channel(query: str, channel_id: str, max_results: int = 5) -> list[dict]:
    """Search within a specific channel."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "channelId": channel_id,
        "type": "video",
        "maxResults": max_results,
        "order": "relevance",
        "key": YOUTUBE_API_KEY,
    }

    try:
        # Rate limit YouTube API calls
        wait_for_youtube()

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        videos = []
        for item in data.get("items", []):
            videos.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "channel_id": item["snippet"]["channelId"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "published_at": item["snippet"]["publishedAt"],
            })
        
        return videos
        
    except requests.RequestException as e:
        print(f"❌ Channel search error: {e}")
        return []


def _enrich_with_stats(videos: list[dict]) -> list[dict]:
    """Add view count, like count, and duration to videos."""
    if not videos:
        return videos
    
    video_ids = ",".join([v["id"] for v in videos])
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics,contentDetails",
        "id": video_ids,
        "key": YOUTUBE_API_KEY,
    }

    try:
        # Rate limit YouTube API calls
        wait_for_youtube()

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        stats_map = {}
        for item in data.get("items", []):
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            stats_map[item["id"]] = {
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "duration": content.get("duration", "PT0M0S"),
            }
        
        for video in videos:
            if video["id"] in stats_map:
                video.update(stats_map[video["id"]])
        
        return videos
        
    except requests.RequestException as e:
        print(f"⚠️  Stats enrichment error: {e}")
        return videos


def evaluate_video_relevance(
    videos: list[dict],
    keyword: str,
    article_title: str,
    article_summary: str = ""
) -> list[dict]:
    """
    Use Claude to evaluate and score video relevance to the article.
    
    Args:
        videos: List of video dictionaries from YouTube search
        keyword: Article's primary keyword
        article_title: Article title
        article_summary: Brief summary of article content
        
    Returns:
        Videos sorted by relevance score, with scores added
    """
    if not videos:
        return []
    
    if not ANTHROPIC_API_KEY:
        print("⚠️  ANTHROPIC_API_KEY not set - skipping relevance evaluation")
        return videos[:MAX_VIDEOS_PER_ARTICLE]
    
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Prepare video list for evaluation
    video_list = "\n".join([
        f"{i+1}. \"{v['title']}\" by {v['channel']}\n   Description: {v['description'][:200]}..."
        for i, v in enumerate(videos)
    ])
    
    prompt = f"""Evaluate these YouTube videos for relevance to a lawn care article.

ARTICLE DETAILS:
- Keyword: {keyword}
- Title: {article_title}
- Summary: {article_summary or "General lawn care guidance on this topic"}

VIDEOS TO EVALUATE:
{video_list}

For each video, provide:
1. A relevance score (1-10, where 10 is perfectly relevant)
2. Brief reason for the score

SCORING CRITERIA:
- 9-10: Directly addresses the exact topic, educational, from credible source
- 7-8: Closely related, helpful supplementary content
- 5-6: Somewhat related but not ideal match
- 1-4: Off-topic, promotional, or poor quality

Return JSON array with this format:
[
  {{"index": 1, "score": 8.5, "reason": "Directly covers fertilization timing"}},
  {{"index": 2, "score": 6.0, "reason": "General lawn care, not specific to topic"}}
]

Only return the JSON array, no other text."""

    try:
        # Rate limit Claude API calls
        wait_for_claude()

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = response.content[0].text.strip()
        
        # Clean up response if needed
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        evaluations = json.loads(response_text)
        
        # Add scores to videos
        for eval_item in evaluations:
            idx = eval_item["index"] - 1
            if 0 <= idx < len(videos):
                videos[idx]["relevance_score"] = eval_item["score"]
                videos[idx]["relevance_reason"] = eval_item["reason"]
        
        # Sort by relevance score
        videos.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return videos
        
    except Exception as e:
        print(f"⚠️  Relevance evaluation error: {e}")
        # Return top videos by view count as fallback
        videos.sort(key=lambda x: x.get("view_count", 0), reverse=True)
        return videos


def _fetch_transcript_supadata(video_id: str) -> Optional[str]:
    """
    Fallback: Fetch transcript using SupaData API.

    Args:
        video_id: YouTube video ID

    Returns:
        Full transcript text or None if unavailable
    """
    if not SUPADATA_API_KEY:
        print(f"   ⚠️  SUPADATA_API_KEY not set - cannot use fallback")
        return None

    try:
        response = requests.get(
            f"https://api.supadata.ai/v1/youtube/transcript?video_id={video_id}",
            headers={"x-api-key": SUPADATA_API_KEY},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("content"):
                # SupaData returns content as list of segments or string
                content = data["content"]
                if isinstance(content, list):
                    return " ".join([seg.get("text", "") for seg in content])
                return str(content)

        return None

    except Exception as e:
        print(f"   ⚠️  SupaData transcript error: {e}")
        return None


def fetch_transcript(video_id: str) -> Optional[str]:
    """
    Fetch the transcript for a YouTube video.
    Uses YouTube Transcript API as primary, SupaData as fallback.

    Args:
        video_id: YouTube video ID

    Returns:
        Full transcript text or None if unavailable
    """
    # Primary: YouTube Transcript API
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id)

        # Combine all transcript segments into full text
        full_text = " ".join([segment.text for segment in transcript_list])
        return full_text

    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"   ⚠️  No transcript via YouTube API for {video_id}: {type(e).__name__}")
        print(f"   🔄 Trying SupaData fallback...")
        return _fetch_transcript_supadata(video_id)
    except Exception as e:
        print(f"   ⚠️  Transcript fetch error for {video_id}: {e}")
        print(f"   🔄 Trying SupaData fallback...")
        return _fetch_transcript_supadata(video_id)


def extract_transcript_insights(
    transcript: str,
    keyword: str,
    article_title: str,
    video_title: str
) -> dict:
    """
    Use Claude to extract key insights from a video transcript.

    Returns:
        dict with 'key_points', 'quotes', 'tips', 'keywords'
    """
    if not ANTHROPIC_API_KEY or not transcript:
        return {}

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    # Truncate transcript if too long (keep first ~8000 chars)
    truncated = transcript[:8000] if len(transcript) > 8000 else transcript

    prompt = f"""Analyze this YouTube video transcript and extract insights relevant to the article topic.

ARTICLE: {article_title}
KEYWORD: {keyword}
VIDEO: {video_title}

TRANSCRIPT:
{truncated}

Extract and return JSON with:
1. "key_points": 3-5 main actionable tips from the video (brief, 1 sentence each)
2. "best_quote": One compelling direct quote from the transcript (verbatim, 1-2 sentences)
3. "pro_tips": 2-3 expert tips or insights not commonly known
4. "seo_keywords": 5-8 additional relevant keywords/phrases mentioned
5. "timestamp_topics": 3-4 main topics with approximate position (early/middle/late in video)

Return ONLY valid JSON, no other text:
{{"key_points": [...], "best_quote": "...", "pro_tips": [...], "seo_keywords": [...], "timestamp_topics": [...]}}"""

    try:
        # Rate limit Claude API calls
        wait_for_claude()

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # Clean up response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        return json.loads(response_text)

    except Exception as e:
        print(f"   ⚠️  Transcript analysis error: {e}")
        return {}


def enrich_videos_with_transcripts(
    videos: list[dict],
    keyword: str,
    article_title: str
) -> list[dict]:
    """
    Fetch transcripts and extract insights for selected videos.

    Args:
        videos: List of video dicts (already filtered by relevance)
        keyword: Article keyword
        article_title: Article title

    Returns:
        Videos enriched with transcript data and insights
    """
    for video in videos:
        print(f"   📝 Fetching transcript for: {video['title'][:40]}...")

        transcript = fetch_transcript(video["id"])

        if transcript:
            video["has_transcript"] = True
            video["transcript_length"] = len(transcript)

            # Extract insights
            insights = extract_transcript_insights(
                transcript, keyword, article_title, video["title"]
            )

            if insights:
                video["insights"] = insights
                print(f"      ✅ Extracted {len(insights.get('key_points', []))} key points")
        else:
            video["has_transcript"] = False

    return videos


def find_videos_for_article(
    keyword: str,
    article_title: str,
    article_summary: str = "",
    use_curated_only: bool = False,
    min_score: float = MIN_RELEVANCE_SCORE,
    max_videos: int = MAX_VIDEOS_PER_ARTICLE,
    fetch_transcripts: bool = True,
    use_cache: bool = True,
    force_refresh: bool = False
) -> list[dict]:
    """
    Main function: Find the best YouTube videos for an article.

    Args:
        keyword: Article's primary keyword
        article_title: Article title
        article_summary: Brief summary of article content
        use_curated_only: Only search curated channels
        min_score: Minimum relevance score to include (default 7.0)
        max_videos: Maximum videos to return (default 2)
        fetch_transcripts: Whether to fetch and analyze transcripts
        use_cache: Whether to use cached results (default True)
        force_refresh: Force refresh even if cache exists (default False)

    Returns:
        List of 0-2 video dictionaries with relevance scores
    """
    print(f"\n🔍 Searching YouTube for: {keyword}")

    # Check cache first (unless force_refresh)
    if use_cache and not force_refresh:
        cached = get_cached_videos(keyword, article_title)
        if cached is not None:
            return cached

    # Step 1: Search YouTube
    videos = search_youtube(keyword, use_curated_only=use_curated_only)
    
    if not videos:
        print("   No videos found")
        return []
    
    print(f"   Found {len(videos)} videos, evaluating relevance...")
    
    # Step 2: Evaluate relevance with AI
    videos = evaluate_video_relevance(
        videos, keyword, article_title, article_summary
    )
    
    # Step 3: Filter by minimum score
    qualified = [v for v in videos if v.get("relevance_score", 0) >= min_score]
    
    if not qualified:
        print(f"   No videos met minimum relevance score ({min_score})")
        return []
    
    # Step 4: Get top videos
    result = qualified[:max_videos]

    for v in result:
        print(f"   ✅ {v['title'][:50]}... (score: {v.get('relevance_score', 'N/A')})")

    # Step 5: Fetch transcripts and extract insights (optional)
    if fetch_transcripts and result:
        print(f"   📝 Fetching transcripts...")
        result = enrich_videos_with_transcripts(result, keyword, article_title)

    # Step 6: Cache results for future use
    if use_cache and result:
        cache_videos(keyword, article_title, result)

    return result


def format_video_for_frontmatter(video: dict) -> dict:
    """Format video data for article frontmatter."""
    data = {
        "id": video["id"],
        "title": video["title"],
        "channel": video["channel"],
        "thumbnail": video.get("thumbnail", ""),
        "relevance_score": video.get("relevance_score", 0),
    }

    # Include insights if available
    if video.get("insights"):
        data["insights"] = video["insights"]
        data["has_transcript"] = video.get("has_transcript", False)

    return data


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_search.py <keyword>")
        print("Example: python youtube_search.py 'best time to fertilize lawn'")
        sys.exit(1)
    
    keyword = " ".join(sys.argv[1:])
    
    videos = find_videos_for_article(
        keyword=keyword,
        article_title=f"Guide to {keyword.title()}",
        article_summary=""
    )
    
    if videos:
        print("\n" + "="*60)
        print("RESULTS:")
        print("="*60)
        for i, v in enumerate(videos, 1):
            print(f"\n{i}. {v['title']}")
            print(f"   Channel: {v['channel']}")
            print(f"   Score: {v.get('relevance_score', 'N/A')}")
            print(f"   Reason: {v.get('relevance_reason', 'N/A')}")
            print(f"   URL: https://youtube.com/watch?v={v['id']}")
            print(f"   Views: {v.get('view_count', 0):,}")
    else:
        print("\nNo suitable videos found.")
