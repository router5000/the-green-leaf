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

# Cannabis topic bank organized by season (outdoor growing calendar) + evergreen clusters
CANNABIS_TOPICS = {
    # Spring: germination, seedlings, transplanting outdoors, strain selection
    "spring": [
        "how to germinate cannabis seeds",
        "cannabis seedling care guide",
        "when to transplant cannabis outdoors",
        "best cannabis strains for outdoor growing",
        "how to sex cannabis plants",
        "cannabis seedling light schedule",
        "starting cannabis seeds indoors",
        "feminized vs autoflower seeds explained",
        "cannabis germination rate tips",
        "best soil mix for cannabis seedlings",
        "how to harden off cannabis plants",
        "cloning cannabis plants beginners guide",
        "cannabis companion planting guide",
        "organic cannabis soil preparation",
        "cannabis grow calendar spring checklist",
    ],
    # Summer: vegetative training, nutrients, pest/disease management
    "summer": [
        "cannabis vegetative stage nutrients guide",
        "how to top cannabis plants",
        "low stress training LST cannabis guide",
        "SCROG method for cannabis explained",
        "cannabis watering schedule guide",
        "how to identify cannabis nutrient deficiencies",
        "cannabis pH and EC guide",
        "fimming vs topping cannabis plants",
        "cannabis defoliation techniques",
        "how to identify cannabis pests",
        "spider mites on cannabis treatment",
        "cannabis root development guide",
        "super cropping cannabis technique",
        "cannabis nitrogen deficiency vs light burn",
        "outdoor cannabis training techniques",
    ],
    # Fall: harvest, drying, curing — peak search season
    "fall": [
        "when to harvest cannabis plants",
        "how to read cannabis trichomes for harvest",
        "cannabis flushing before harvest guide",
        "how to dry cannabis buds properly",
        "cannabis curing guide for beginners",
        "wet trimming vs dry trimming cannabis",
        "cannabis harvest checklist outdoor",
        "how long to cure cannabis",
        "cannabis storage after curing",
        "how to trim cannabis buds",
        "cannabis drying room setup",
        "cannabis brix levels and harvest timing",
        "how to increase cannabis terpenes at harvest",
        "cannabis yield per plant outdoor",
        "cannabis bud rot prevention and treatment",
    ],
    # Winter: indoor growing, lights, hydroponics, autoflowers
    "winter": [
        "indoor cannabis growing guide for beginners",
        "best LED grow lights for cannabis 2026",
        "cannabis grow tent setup guide",
        "hydroponic cannabis growing DWC guide",
        "autoflower cannabis grow guide",
        "cannabis grow room ventilation setup",
        "cannabis light cycle for flowering",
        "best cannabis nutrients for indoor growing",
        "cannabis coco coir growing guide",
        "how to control humidity in cannabis grow room",
        "cannabis cloning success rate tips",
        "cannabis sea of green SOG method",
        "LED vs HPS grow lights for cannabis",
        "cannabis VPD chart explained",
        "cannabis grow journal how to start",
    ],
    # Evergreen education — foundational, high-volume, durable traffic
    "evergreen": [
        "indica vs sativa vs hybrid explained",
        "cannabis for beginners complete guide",
        "how does THC affect the brain",
        "what is CBD and how does it work",
        "cannabis consumption methods compared",
        "how to dose cannabis edibles safely",
        "cannabis tolerance explained",
        "how to store cannabis properly",
        "cannabis and alcohol interaction",
        "cannabis entourage effect explained",
        "how to roll a joint step by step",
        "cannabis tincture how to use",
        "cannabis microdosing guide",
        "cannabis drug test how long does it stay",
        "first time cannabis user tips",
        "cannabis smoke vs vaporize comparison",
        "cannabis allergy symptoms and causes",
        "how to make cannabis tea",
        "cannabis edibles vs smoking onset time",
        "cannabis tolerance break benefits",
    ],
    # Strain guides — high affiliate potential (seed banks), perennial curiosity
    "strains": [
        "best strains for anxiety and stress",
        "best cannabis strains for sleep",
        "best strains for chronic pain relief",
        "best sativa strains for energy and focus",
        "best indica strains for relaxation",
        "high CBD low THC strains guide",
        "Blue Dream strain effects and review",
        "OG Kush strain guide and effects",
        "Girl Scout Cookies strain review",
        "Gorilla Glue strain effects guide",
        "Wedding Cake strain review",
        "Gelato strain effects and terpenes",
        "Jack Herer strain review",
        "Northern Lights strain guide",
        "Granddaddy Purple strain effects",
        "Sour Diesel strain effects review",
        "best strains for creativity",
        "best strains for nausea and appetite",
        "best cannabis strains for depression",
        "high THC strains list 2026",
    ],
    # Growing equipment/products — strong affiliate (Mars Hydro, AC Infinity, Fox Farm, etc.)
    "growing": [
        "best cannabis grow lights under $200",
        "AC Infinity vs other inline fans review",
        "Fox Farm vs General Hydroponics nutrients",
        "best cannabis growing medium comparison",
        "cannabis grow tent brands compared",
        "best carbon filter for grow tent",
        "smart cannabis grow controllers review",
        "best cannabis fertilizer for beginners",
        "cannabis pH meters comparison",
        "best pots for cannabis growing",
        "cannabis grow light coverage calculator",
        "best cannabis seeds to buy online",
        "autoflower vs photoperiod cannabis comparison",
        "cannabis seedling heat mat guide",
        "best humidity controller for grow room",
    ],
    # Wellness and health — medical cannabis, CBD, research-backed claims
    "wellness": [
        "cannabis for anxiety research and evidence",
        "CBD oil for pain management guide",
        "medical cannabis conditions it treats",
        "cannabis and sleep quality research",
        "cannabis for inflammation and arthritis",
        "microdosing cannabis for mental health",
        "cannabis and PTSD treatment research",
        "CBD dosage guide by weight",
        "cannabis for nausea and chemotherapy",
        "cannabis and exercise recovery",
        "cannabis for migraines evidence",
        "CBD vs THC for anxiety which is better",
        "cannabis and epilepsy CBD research",
        "cannabis harm reduction guide",
        "cannabis dependency signs and prevention",
    ],
    # Legal and policy — high news-driven traffic, low competition educational content
    "legal": [
        "cannabis legalization by state 2026",
        "recreational cannabis states list",
        "cannabis possession limits by state",
        "how to get a medical cannabis card",
        "cannabis social equity programs explained",
        "cannabis expungement how it works",
        "cannabis DUI laws by state",
        "traveling with cannabis laws guide",
        "cannabis home grow laws by state",
        "cannabis employment drug testing laws",
        "cannabis banking laws SAFE Act explained",
        "federal cannabis legalization timeline",
        "cannabis licensing requirements by state",
        "cannabis delivery service laws",
        "cannabis gifting laws explained",
    ],
    # Science and cannabinoids — attracts educated readers, strong SEO authority signal
    "science": [
        "cannabis terpenes complete guide and effects",
        "THC vs CBD vs CBN vs CBG explained",
        "THCA vs THC what is the difference",
        "cannabis cannabinoids full list and effects",
        "myrcene terpene effects and strains",
        "limonene terpene cannabis effects",
        "beta-caryophyllene terpene guide",
        "linalool terpene cannabis effects",
        "pinene terpene effects cannabis",
        "cannabis endocannabinoid system explained",
        "cannabis pharmacology how it works",
        "THCV effects and benefits guide",
        "CBC cannabinoid effects explained",
        "cannabis terpene profiles by strain",
        "cannabis extraction methods compared",
    ],
}


def get_current_season() -> str:
    """Determine current season based on Northern Hemisphere dates."""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def get_relevant_seasons() -> list[str]:
    """Get topic buckets relevant for content planning (current season + upcoming + evergreen + always-on clusters)."""
    season_order = ["spring", "summer", "fall", "winter"]
    current = get_current_season()
    current_idx = season_order.index(current)
    next_idx = (current_idx + 1) % 4

    # Always pull from cluster banks — evergreen commercial-intent buckets
    # not bound to a single season.
    always_on_clusters = ["strains", "growing", "wellness", "legal", "products", "science"]

    return [current, season_order[next_idx], "evergreen"] + always_on_clusters


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


def get_google_trends_interest(keywords: list[str]) -> dict[str, int]:
    """
    Get relative interest scores from Google Trends.
    Returns dict of keyword -> interest score (0-100).
    """
    if not PYTRENDS_AVAILABLE:
        # Return equal scores if pytrends not available
        return {kw: 50 for kw in keywords}
    
    interest_scores = {}
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Google Trends only allows 5 keywords at a time
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        try:
            pytrends.build_payload(batch, cat=0, timeframe='today 3-m', geo='US')
            interest_over_time = pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                for kw in batch:
                    if kw in interest_over_time.columns:
                        # Get average interest over the period
                        interest_scores[kw] = int(interest_over_time[kw].mean())
                    else:
                        interest_scores[kw] = 0
            else:
                for kw in batch:
                    interest_scores[kw] = 0
                    
        except Exception as e:
            print(f"Google Trends error for batch {batch}: {e}")
            for kw in batch:
                interest_scores[kw] = 50  # Default score on error
    
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
    
    # Get relevant seasons
    if force_season:
        seasons = [force_season, "evergreen"]
    else:
        seasons = get_relevant_seasons()
    
    print(f"📅 Targeting seasons: {', '.join(seasons)}")
    
    # Gather candidate keywords
    candidates = []
    for season in seasons:
        relevance = 1.0 if season == seasons[0] else (0.8 if season == "evergreen" else 0.6)
        for kw in CANNABIS_TOPICS.get(season, []):
            candidates.append({
                "keyword": kw,
                "season": season,
                "season_relevance": relevance
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

    pytrends = TrendReq(hl='en-US', tz=360)
    trending = []

    seed_terms = ["cannabis", "marijuana strains", "CBD oil", "cannabis growing"]

    for term in seed_terms:
        try:
            pytrends.build_payload([term], cat=0, timeframe='today 1-m', geo='US')
            related = pytrends.related_queries()

            if term in related and related[term]["rising"] is not None:
                rising = related[term]["rising"]
                for _, row in rising.head(5).iterrows():
                    query = row["query"]
                    if any(word in query.lower() for word in [
                        "cannabis", "marijuana", "weed", "cbd", "thc",
                        "strain", "hemp", "dispensary", "edible", "terpene"
                    ]):
                        trending.append(query)

        except Exception as e:
            print(f"Error getting related queries for {term}: {e}")

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
