#!/usr/bin/env python3
"""
Keyword Research Module for The Green Leaf Cannabis Content Engine

Uses Google Trends API (free) with optional Keywords Everywhere API for search volume.
Intelligently selects keywords based on:
- Seasonal relevance (outdoor growing seasons)
- Trending interest
- Competition (avoiding already-published topics)
- Search volume (if Keywords Everywhere API key provided)
"""

import os
import json
import re
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import requests

# Google Trends unofficial API (pytrends)
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("Warning: pytrends not installed. Run: pip install pytrends")

from dotenv import load_dotenv

# Content calendar for topic balancing
try:
    from content_calendar import get_balanced_keyword_recommendations, should_publish
    CONTENT_CALENDAR_AVAILABLE = True
except ImportError:
    CONTENT_CALENDAR_AVAILABLE = False

load_dotenv()

# Configuration
KEYWORDS_EVERYWHERE_API_KEY = os.getenv("KEYWORDS_EVERYWHERE_API_KEY")  # Optional
SITE_CONTENT_PATH = Path("site/content/posts")
KEYWORD_CACHE_PATH = Path(".cache/keyword_cache.json")
CACHE_TTL_HOURS = 24

# Content pillars organized by editorial focus (not growing season)
CONTENT_PILLARS = {
    # Pillar 1: Individual strain profiles — deep, high-affiliate, high search volume
    "strain_database": [
        "Blue Dream strain effects and review",
        "OG Kush strain guide and terpenes",
        "Girl Scout Cookies strain profile",
        "Gorilla Glue 4 strain review",
        "Wedding Cake strain effects guide",
        "Gelato strain review and terpenes",
        "Jack Herer strain guide",
        "Northern Lights strain profile",
        "Granddaddy Purple strain effects",
        "Sour Diesel strain review",
        "White Widow strain effects and lineage",
        "AK-47 strain guide and effects",
        "Amnesia Haze strain profile",
        "Pineapple Express strain review",
        "Purple Haze strain effects guide",
        "Zkittlez strain review and terpenes",
        "Runtz strain effects and lineage",
        "MAC 1 strain guide",
        "Cereal Milk strain review",
        "Ice Cream Cake strain review",
        "London Pound Cake strain guide",
        "Do-Si-Dos strain effects profile",
        "Mimosa strain review and terpenes",
        "Tropicana Cookies strain guide",
        "Apple Fritter strain effects",
        "Banana Runtz strain review",
        "Sherbet strain effects and terpenes",
        "Biscotti strain guide and effects",
        "Gary Payton strain effects profile",
        "Durban Poison strain guide",
        "Trainwreck strain review",
        "Super Lemon Haze strain effects",
        "Strawberry Cough strain guide",
        "Green Crack strain effects profile",
        "Skywalker OG strain review",
        "Bubba Kush strain guide and effects",
        "Purple Punch strain effects review",
        "Zkittlez strain guide",
        "Animal Cookies strain review",
        "Chemdawg strain guide and lineage",
    ],
    # Pillar 2: Strain discovery roundups — high-volume, commercial-intent
    "strain_discovery": [
        "best indica strains for sleep 2026",
        "best strains for anxiety and stress",
        "best sativa strains for energy and focus",
        "high CBD low THC strains guide",
        "strongest THC strains 2026",
        "best strains for creativity and focus",
        "best strains for chronic pain relief",
        "best strains for depression",
        "best strains for nausea",
        "best cannabis strains for beginners",
        "best hybrid strains 2026",
        "best terpene-rich strains guide",
        "best strains for social anxiety",
        "best daytime cannabis strains",
        "best nighttime cannabis strains",
        "best strains for appetite stimulation",
        "best strains for relaxation without sedation",
        "most popular cannabis strains 2026",
        "top 10 cannabis strains 2026",
        "best cannabis strains for migraines",
        "best strains for inflammation and arthritis",
        "cannabis strains high in myrcene",
        "cannabis strains high in limonene",
        "cannabis strains high in linalool",
        "best strains for euphoria and happiness",
        "best strains for PTSD",
        "best CBD-dominant strains guide",
        "best strains for focus and ADHD",
        "best strains for insomnia",
        "best autoflower strains to buy 2026",
    ],
    # Pillar 3: Cannabis education — foundational, evergreen, AI-citation friendly
    "cannabis_education": [
        "indica vs sativa vs hybrid explained",
        "cannabis terpenes complete guide",
        "THC vs CBD vs CBN vs CBG explained",
        "entourage effect explained",
        "how to read cannabis lab results",
        "THCA vs THC what is the difference",
        "cannabis endocannabinoid system explained",
        "myrcene terpene effects and strains",
        "limonene terpene cannabis effects",
        "beta-caryophyllene terpene guide",
        "linalool terpene cannabis effects",
        "pinene terpene effects cannabis",
        "terpinolene terpene guide",
        "cannabis tolerance explained",
        "how THC affects the brain",
        "how to dose cannabis safely",
        "cannabis for beginners complete guide",
        "what are cannabis flavonoids",
        "THCV effects and benefits explained",
        "cannabis pharmacology explained",
        "what does cannabis potency mean",
        "understanding cannabis certificates of analysis",
        "cannabis and sleep science explained",
        "cannabis and anxiety the research",
        "THC to CBD ratio guide",
        "cannabis microdosing guide",
        "CBD bioavailability by consumption method",
        "cannabis drug interactions guide",
        "full spectrum vs broad spectrum CBD explained",
        "what is the difference between hemp and cannabis",
    ],
    # Pillar 4: Reviews and culture — consumption methods, consumer guides, lifestyle
    "reviews_culture": [
        "how to choose the right cannabis strain",
        "cannabis consumption methods compared",
        "vaping vs smoking cannabis comparison",
        "cannabis edibles vs smoking onset times",
        "how to read a dispensary menu",
        "cannabis tinctures how to use",
        "how to store cannabis properly",
        "what to expect first time cannabis user",
        "best cannabis vaporizers 2026",
        "cannabis gummies vs capsules comparison",
        "cannabis topicals how they work",
        "cannabis concentrates for beginners",
        "what is live resin vs cured resin",
        "what is rosin vs resin",
        "cannabis hash types explained",
        "what is THCA flower",
        "cannabis pre-rolls buying guide",
        "how to talk to a budtender",
        "cannabis tolerance break guide",
        "how to choose CBD products",
        "cannabis third-party testing why it matters",
        "cannabis topicals vs edibles for pain",
        "cannabis infused beverages guide",
        "how to read cannabis packaging",
        "dispensary vs delivery service guide",
        "cannabis moon rocks what are they",
        "cannabis terpene profiles by strain",
        "cannabis extraction methods compared",
        "dabbing cannabis concentrates guide",
        "cannabis sublingual vs ingested effects",
    ],
}


def get_content_pillars() -> list[str]:
    """Return all content pillars. All pillars are weighted equally — strain content is evergreen."""
    return list(CONTENT_PILLARS.keys())


def get_published_keywords() -> set[str]:
    """Extract keywords from already-published articles to avoid duplicates."""
    published = set()
    
    if not SITE_CONTENT_PATH.exists():
        return published
    
    for md_file in SITE_CONTENT_PATH.glob("*.md"):
        try:
            content = md_file.read_text()
            # Extract keyword from frontmatter
            match = re.search(r'^keyword:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
            if match:
                published.add(match.group(1).lower().strip())
            
            # Also extract title to avoid similar topics
            title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
            if title_match:
                # Normalize title for comparison
                title_words = set(title_match.group(1).lower().split())
                published.update(title_words)
        except Exception as e:
            print(f"Warning: Could not parse {md_file}: {e}")
    
    return published


def load_cache() -> dict:
    """Load keyword cache if exists and not expired."""
    if not KEYWORD_CACHE_PATH.exists():
        return {}
    
    try:
        cache = json.loads(KEYWORD_CACHE_PATH.read_text())
        cache_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
        if datetime.now() - cache_time < timedelta(hours=CACHE_TTL_HOURS):
            return cache
    except Exception:
        pass
    
    return {}


def save_cache(data: dict):
    """Save keyword data to cache."""
    KEYWORD_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["timestamp"] = datetime.now().isoformat()
    KEYWORD_CACHE_PATH.write_text(json.dumps(data, indent=2))


# Google Trends rate-limiting controls.
# Trends has no official API and aggressively returns HTTP 429 when requests
# from one IP come too fast — which is exactly what happened in CI, where every
# batch failed. We (a) space requests out with a jittered delay, and (b) retry
# with exponential backoff when a request is throttled.
TRENDS_BATCH_DELAY = (4.0, 8.0)   # (min, max) seconds of jittered pause between requests
TRENDS_MAX_RETRIES = 2            # attempts per request before giving up
TRENDS_BACKOFF_BASE = 5.0         # seconds; backoff is base * 2**attempt (+jitter)

# Circuit breaker: when the whole run's IP is rate-limited (the CI norm, per
# the incident above), retrying every one of the ~26 batches burns 15+ minutes
# for a signal that only accounts for 30% of the keyword score and already
# falls back to a neutral score on failure. After this many CONSECUTIVE
# batches exhaust their retries, stop calling Trends for the rest of this run
# and default the remaining keywords to neutral immediately.
TRENDS_CIRCUIT_BREAKER_THRESHOLD = 3


def _make_trends_client() -> "TrendReq":
    """
    Build a TrendReq.

    Note: we deliberately do NOT pass retries=/backoff_factor= here. When those
    are set, this pytrends version builds urllib3.Retry(..., method_whitelist=...),
    and method_whitelist was removed in urllib3 2.x (renamed to allowed_methods) —
    so every request raises TypeError on urllib3>=2. Retry/backoff is handled at
    the application level by _trends_request_with_backoff() instead.
    """
    return TrendReq(hl='en-US', tz=360, timeout=(10, 30))


def _trends_request_with_backoff(fn, label: str):
    """
    Run a pytrends call, retrying with exponential backoff on rate-limit / transient
    errors. Returns the call result, or None if all retries are exhausted.
    """
    for attempt in range(TRENDS_MAX_RETRIES):
        try:
            return fn()
        except Exception as e:
            is_rate_limited = "429" in str(e) or "rate" in str(e).lower() or "too many" in str(e).lower()
            if attempt == TRENDS_MAX_RETRIES - 1:
                print(f"Google Trends gave up on {label} after {TRENDS_MAX_RETRIES} attempts: {e}")
                return None
            wait = TRENDS_BACKOFF_BASE * (2 ** attempt) + random.uniform(0, 2)
            reason = "rate limited (429)" if is_rate_limited else f"error: {e}"
            print(f"Google Trends {reason} on {label}; retrying in {wait:.1f}s "
                  f"(attempt {attempt + 1}/{TRENDS_MAX_RETRIES})")
            time.sleep(wait)
    return None


def get_google_trends_interest(keywords: list[str]) -> dict[str, int]:
    """
    Get relative interest scores from Google Trends.
    Returns dict of keyword -> interest score (0-100).
    """
    if not PYTRENDS_AVAILABLE:
        # Return equal scores if pytrends not available
        return {kw: 50 for kw in keywords}

    interest_scores = {}
    pytrends = _make_trends_client()

    # Google Trends only allows 5 keywords at a time
    batches = [keywords[i:i+5] for i in range(0, len(keywords), 5)]
    consecutive_failures = 0
    circuit_open = False
    for batch_idx, batch in enumerate(batches):
        if circuit_open:
            # Trends has failed too many times in a row this run — assume the
            # IP is rate-limited for the whole run and stop paying the retry
            # tax on every remaining batch.
            for kw in batch:
                interest_scores[kw] = 50
            continue

        # Pause between requests (skip before the first) to avoid tripping 429.
        if batch_idx > 0:
            time.sleep(random.uniform(*TRENDS_BATCH_DELAY))

        def _fetch():
            pytrends.build_payload(batch, cat=0, timeframe='today 3-m', geo='US')
            return pytrends.interest_over_time()

        interest_over_time = _trends_request_with_backoff(_fetch, f"batch {batch}")

        if interest_over_time is None:
            # Request failed after retries — fall back to a neutral score.
            for kw in batch:
                interest_scores[kw] = 50  # Default score on error
            consecutive_failures += 1
            if consecutive_failures >= TRENDS_CIRCUIT_BREAKER_THRESHOLD:
                remaining = len(batches) - batch_idx - 1
                print(f"Google Trends failed {consecutive_failures} batches in a row — "
                      f"assuming this run's IP is rate-limited and skipping the "
                      f"remaining {remaining} batch(es) (defaulting to neutral score).")
                circuit_open = True
        elif not interest_over_time.empty:
            for kw in batch:
                if kw in interest_over_time.columns:
                    # Get average interest over the period
                    interest_scores[kw] = int(interest_over_time[kw].mean())
                else:
                    interest_scores[kw] = 0
        else:
            for kw in batch:
                interest_scores[kw] = 0

    return interest_scores


def get_keywords_everywhere_volume(keywords: list[str]) -> dict[str, int]:
    """
    Get search volume from Keywords Everywhere API.
    Requires API key (~$10 for 100k credits).
    Returns dict of keyword -> monthly search volume.
    """
    if not KEYWORDS_EVERYWHERE_API_KEY:
        return {}
    
    url = "https://api.keywordseverywhere.com/v1/get_keyword_data"
    headers = {
        "Authorization": f"Bearer {KEYWORDS_EVERYWHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    volumes = {}
    
    # API allows up to 100 keywords per request
    for i in range(0, len(keywords), 100):
        batch = keywords[i:i+100]
        try:
            response = requests.post(url, headers=headers, json={
                "country": "us",
                "currency": "USD",
                "dataSource": "gkp",
                "kw": batch
            })
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", []):
                    volumes[item["keyword"]] = item.get("vol", 0)
            else:
                print(f"Keywords Everywhere API error: {response.status_code}")
                
        except Exception as e:
            print(f"Keywords Everywhere error: {e}")
    
    return volumes


def score_keyword(
    keyword: str,
    trends_score: int,
    search_volume: int,
    season_relevance: float,
    is_published: bool
) -> float:
    """
    Calculate composite score for keyword prioritization.
    
    Scoring weights:
    - Trends interest: 30%
    - Search volume: 30% (normalized)
    - Seasonal relevance: 30%
    - Novelty bonus: 10%
    """
    if is_published:
        return 0  # Skip already published topics
    
    # Normalize trends (0-100 -> 0-1)
    trends_normalized = trends_score / 100
    
    # Normalize search volume (log scale, 100-10k sweet spot)
    if search_volume > 0:
        import math
        # Sweet spot: 100-10,000 monthly searches
        vol_log = math.log10(max(search_volume, 1))
        vol_normalized = min(vol_log / 4, 1)  # Cap at 10,000
    else:
        vol_normalized = 0.5  # Default if no volume data
    
    # Calculate composite score
    score = (
        (trends_normalized * 0.30) +
        (vol_normalized * 0.30) +
        (season_relevance * 0.30) +
        (0.10)  # Novelty bonus for unpublished
    )
    
    return round(score, 3)


def find_best_keyword(
    count: int = 1,
    use_cache: bool = True,
    force_season: Optional[str] = None
) -> list[dict]:
    """
    Find the best keyword(s) to write about.
    
    Args:
        count: Number of keywords to return
        use_cache: Whether to use cached results
        force_season: Override automatic season detection
    
    Returns:
        List of dicts with keyword data, sorted by score
    """
    print("🔍 Starting keyword research...")
    
    # Check cache first
    if use_cache:
        cache = load_cache()
        if cache.get("keywords"):
            print("📦 Using cached keyword data")
            return cache["keywords"][:count]

    # Get content pillars to draw from
    if force_season:
        pillars = [force_season] if force_season in CONTENT_PILLARS else get_content_pillars()
    else:
        pillars = get_content_pillars()

    print(f"📋 Targeting pillars: {', '.join(pillars)}")

    # Gather candidate keywords — all pillars equal weight (strain content is evergreen)
    candidates = []
    for pillar in pillars:
        for kw in CONTENT_PILLARS.get(pillar, []):
            candidates.append({
                "keyword": kw,
                "season": "evergreen",
                "season_relevance": 1.0
            })
    
    print(f"📋 Evaluating {len(candidates)} candidate keywords...")
    
    # Get published keywords to exclude
    published = get_published_keywords()
    print(f"📰 Found {len(published)} published keywords/topics to exclude")
    
    # Get Google Trends data
    keywords = [c["keyword"] for c in candidates]
    print("📈 Fetching Google Trends data...")
    trends_scores = get_google_trends_interest(keywords)
    
    # Get search volume (if API key available)
    volumes = {}
    if KEYWORDS_EVERYWHERE_API_KEY:
        print("🔢 Fetching search volume data...")
        volumes = get_keywords_everywhere_volume(keywords)
    
    # Score all candidates
    results = []
    for candidate in candidates:
        kw = candidate["keyword"]
        kw_lower = kw.lower()
        
        # Check if already published (keyword or significant word overlap)
        kw_words = set(kw_lower.split())
        is_published = (
            kw_lower in published or
            len(kw_words & published) >= 3  # 3+ word overlap
        )
        
        score = score_keyword(
            keyword=kw,
            trends_score=trends_scores.get(kw, 50),
            search_volume=volumes.get(kw, 0),
            season_relevance=candidate["season_relevance"],
            is_published=is_published
        )
        
        results.append({
            "keyword": kw,
            "season": candidate["season"],
            "score": score,
            "trends_interest": trends_scores.get(kw, 50),
            "search_volume": volumes.get(kw, "N/A"),
            "is_published": is_published
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Filter out published
    unpublished = [r for r in results if not r["is_published"]]

    # Apply content calendar balancing to promote topic diversity
    if CONTENT_CALENDAR_AVAILABLE and unpublished:
        print("⚖️  Applying topic balance adjustments...")
        unpublished = get_balanced_keyword_recommendations(unpublished)
        # Re-sort by adjusted score
        unpublished.sort(key=lambda x: x.get("adjusted_score", x["score"]), reverse=True)

    top_results = unpublished[:count]
    
    # Cache results
    save_cache({"keywords": unpublished[:20]})  # Cache top 20
    
    print(f"\n✅ Top {count} keyword(s) found:")
    for i, result in enumerate(top_results, 1):
        print(f"  {i}. \"{result['keyword']}\"")
        print(f"     Season: {result['season']} | Score: {result['score']}")
        print(f"     Trends: {result['trends_interest']} | Volume: {result['search_volume']}")
        # Show balance info if available
        if "adjusted_score" in result:
            adj = result.get("balance_adjustment", 0)
            adj_str = f"+{adj}" if adj >= 0 else str(adj)
            fills = result.get("fills_gaps", [])
            fills_str = f" | Fills gaps: {', '.join(fills)}" if fills else ""
            print(f"     Balance: {adj_str}{fills_str}")
    
    return top_results


def get_trending_cannabis_topics() -> list[str]:
    """
    Get currently trending cannabis topics from Google Trends.
    Uses related queries feature to discover new topics.
    """
    if not PYTRENDS_AVAILABLE:
        return []

    pytrends = _make_trends_client()
    trending = []

    seed_terms = ["cannabis strains", "best weed strains", "cannabis effects", "marijuana strain review"]

    for term_idx, term in enumerate(seed_terms):
        # Pause between requests (skip before the first) to avoid tripping 429.
        if term_idx > 0:
            time.sleep(random.uniform(*TRENDS_BATCH_DELAY))

        def _fetch():
            pytrends.build_payload([term], cat=0, timeframe='today 1-m', geo='US')
            return pytrends.related_queries()

        related = _trends_request_with_backoff(_fetch, f"related queries for '{term}'")
        if related is None:
            continue

        if term in related and related[term]["rising"] is not None:
            rising = related[term]["rising"]
            for _, row in rising.head(5).iterrows():
                query = row["query"]
                if any(word in query.lower() for word in [
                    "cannabis", "marijuana", "weed", "cbd", "thc",
                    "strain", "hemp", "dispensary", "edible", "terpene"
                ]):
                    trending.append(query)

    return list(set(trending))[:10]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="The Green Leaf Cannabis Keyword Research")
    parser.add_argument("--count", type=int, default=1, help="Number of keywords to find")
    parser.add_argument("--season", type=str, help="Force specific season")
    parser.add_argument("--no-cache", action="store_true", help="Ignore cache")
    parser.add_argument("--trending", action="store_true", help="Show trending topics")

    args = parser.parse_args()

    if args.trending:
        print("\n📈 Discovering trending cannabis topics...")
        trending = get_trending_cannabis_topics()
        if trending:
            print("Trending topics:")
            for topic in trending:
                print(f"  - {topic}")
        else:
            print("No trending topics found (pytrends may not be installed)")
    else:
        results = find_best_keyword(
            count=args.count,
            use_cache=not args.no_cache,
            force_season=args.season
        )
