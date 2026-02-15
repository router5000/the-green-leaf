#!/usr/bin/env python3
"""
Google Search Console Tracking Script

Tracks indexing status, performance metrics, and identifies SEO opportunities
for thegreenleaf.com articles.

Setup:
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download JSON and save as 'gsc_credentials.json' in this directory
4. Enable "Google Search Console API" in your GCP project
5. Run this script - it will open browser for one-time auth

Usage:
    python gsc_tracker.py                    # Full report
    python gsc_tracker.py --indexed-only     # Only show indexed pages
    python gsc_tracker.py --opportunities    # Focus on quick wins
    python gsc_tracker.py --json             # Output as JSON
"""

import os
import json
import glob
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Google API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Constants
SITE_URL = 'sc-domain:thegreenleaf.com'  # Domain property format
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = 'gsc_credentials.json'
TOKEN_FILE = '.gsc_token.json'
CACHE_DIR = '.cache'
REPORT_DIR = 'reports'

# Local paths
POSTS_DIR = 'site/content/posts'
BASE_URL = 'https://thegreenleaf.com'


def get_gsc_service():
    """Authenticate and return GSC API service."""
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"\n❌ Missing {CREDENTIALS_FILE}")
                print("\nSetup instructions:")
                print("1. Go to: https://console.cloud.google.com/apis/credentials")
                print("2. Create OAuth 2.0 Client ID (Desktop application)")
                print("3. Download JSON and save as 'gsc_credentials.json'")
                print("4. Enable 'Google Search Console API' in your GCP project")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('searchconsole', 'v1', credentials=creds)


def get_local_articles():
    """Get all local article slugs and metadata."""
    articles = []
    posts_path = Path(POSTS_DIR)

    for md_file in posts_path.glob('*.md'):
        slug = md_file.stem
        url = f"{BASE_URL}/articles/{slug}"

        # Extract title from frontmatter
        title = slug.replace('-', ' ').title()
        try:
            content = md_file.read_text()
            for line in content.split('\n'):
                if line.startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                    break
        except:
            pass

        articles.append({
            'slug': slug,
            'url': url,
            'title': title,
            'file': str(md_file)
        })

    return articles


def get_performance_data(service, days=28):
    """Fetch performance data from GSC."""
    end_date = datetime.now() - timedelta(days=3)  # GSC data has 3-day lag
    start_date = end_date - timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': ['page'],
                'rowLimit': 1000
            }
        ).execute()

        return response.get('rows', [])
    except Exception as e:
        print(f"Error fetching performance data: {e}")
        return []


def get_keyword_data(service, days=28):
    """Fetch keyword/query data from GSC."""
    end_date = datetime.now() - timedelta(days=3)
    start_date = end_date - timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': ['query', 'page'],
                'rowLimit': 1000
            }
        ).execute()

        return response.get('rows', [])
    except Exception as e:
        print(f"Error fetching keyword data: {e}")
        return []


def analyze_indexing(local_articles, performance_data):
    """Compare local articles against GSC data to determine indexing status."""
    # URLs that have any impressions are definitely indexed
    indexed_urls = set()
    url_metrics = {}

    # Debug: show all URLs from GSC
    if performance_data:
        print("\n   URLs with GSC data:")
        for row in performance_data:
            url = row['keys'][0]
            imp = row.get('impressions', 0)
            print(f"     • {url} ({imp} impressions)")

    for row in performance_data:
        url = row['keys'][0]
        # Normalize URL (remove www, ensure consistent format)
        normalized_url = url.replace('https://www.', 'https://')
        indexed_urls.add(normalized_url)
        url_metrics[normalized_url] = {
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'ctr': row.get('ctr', 0),
            'position': row.get('position', 0),
            'original_url': url  # Keep track of what GSC returned
        }

    indexed = []
    not_indexed = []

    for article in local_articles:
        url = article['url']
        if url in indexed_urls:
            article['metrics'] = url_metrics[url]
            article['status'] = 'indexed'
            indexed.append(article)
        else:
            article['metrics'] = None
            article['status'] = 'not_indexed'
            not_indexed.append(article)

    return indexed, not_indexed


def find_opportunities(keyword_data):
    """Find SEO opportunities from keyword data."""
    opportunities = {
        'striking_distance': [],  # Position 8-20 (page 1-2, almost ranking)
        'low_ctr': [],            # High impressions, low CTR (fix title/meta)
        'quick_wins': []          # Good position + impressions, needs push
    }

    for row in keyword_data:
        query = row['keys'][0]
        page = row['keys'][1]
        clicks = row.get('clicks', 0)
        impressions = row.get('impressions', 0)
        ctr = row.get('ctr', 0)
        position = row.get('position', 100)

        data = {
            'query': query,
            'page': page,
            'clicks': clicks,
            'impressions': impressions,
            'ctr': round(ctr * 100, 2),
            'position': round(position, 1)
        }

        # Striking distance: positions 8-20 with decent impressions
        if 8 <= position <= 20 and impressions >= 10:
            opportunities['striking_distance'].append(data)

        # Low CTR: good position but poor click-through
        if position <= 10 and impressions >= 20 and ctr < 0.03:
            opportunities['low_ctr'].append(data)

        # Quick wins: position 4-10 with good impressions
        if 4 <= position <= 10 and impressions >= 15:
            opportunities['quick_wins'].append(data)

    # Sort each by potential impact
    opportunities['striking_distance'].sort(key=lambda x: x['impressions'], reverse=True)
    opportunities['low_ctr'].sort(key=lambda x: x['impressions'], reverse=True)
    opportunities['quick_wins'].sort(key=lambda x: x['impressions'], reverse=True)

    return opportunities


def generate_report(indexed, not_indexed, opportunities, output_json=False):
    """Generate and print the tracking report."""

    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_articles': len(indexed) + len(not_indexed),
            'indexed': len(indexed),
            'not_indexed': len(not_indexed),
            'index_rate': round(len(indexed) / (len(indexed) + len(not_indexed)) * 100, 1) if indexed or not_indexed else 0
        },
        'indexed_articles': indexed,
        'not_indexed_articles': not_indexed,
        'opportunities': opportunities
    }

    if output_json:
        print(json.dumps(report, indent=2))
        return report

    # Print formatted report
    print("\n" + "="*60)
    print("📊 GSC TRACKING REPORT - thegreenleaf.com")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Summary
    print("\n📈 INDEXING SUMMARY")
    print("-"*40)
    print(f"Total articles:  {report['summary']['total_articles']}")
    print(f"Indexed:         {report['summary']['indexed']} ✅")
    print(f"Not indexed:     {report['summary']['not_indexed']} ⏳")
    print(f"Index rate:      {report['summary']['index_rate']}%")

    # Indexed articles with metrics
    if indexed:
        print("\n✅ INDEXED ARTICLES (with performance)")
        print("-"*40)
        # Sort by impressions
        sorted_indexed = sorted(indexed, key=lambda x: x['metrics']['impressions'], reverse=True)
        for article in sorted_indexed[:15]:  # Top 15
            m = article['metrics']
            print(f"\n  {article['title'][:50]}")
            print(f"    Clicks: {m['clicks']} | Impressions: {m['impressions']} | CTR: {m['ctr']*100:.1f}% | Pos: {m['position']:.1f}")

    # Not indexed
    if not_indexed:
        print(f"\n⏳ NOT INDEXED ({len(not_indexed)} articles)")
        print("-"*40)
        for article in not_indexed[:10]:  # Show first 10
            print(f"  • {article['title'][:55]}")
        if len(not_indexed) > 10:
            print(f"  ... and {len(not_indexed) - 10} more")

    # Opportunities
    print("\n🎯 SEO OPPORTUNITIES")
    print("-"*40)

    if opportunities['striking_distance']:
        print("\n📍 Striking Distance (positions 8-20, almost page 1):")
        for opp in opportunities['striking_distance'][:5]:
            print(f"  • \"{opp['query']}\" - pos {opp['position']} ({opp['impressions']} imp)")

    if opportunities['low_ctr']:
        print("\n📝 Low CTR (fix title/meta description):")
        for opp in opportunities['low_ctr'][:5]:
            print(f"  • \"{opp['query']}\" - {opp['ctr']}% CTR ({opp['impressions']} imp)")

    if opportunities['quick_wins']:
        print("\n🚀 Quick Wins (good position, needs content boost):")
        for opp in opportunities['quick_wins'][:5]:
            print(f"  • \"{opp['query']}\" - pos {opp['position']} ({opp['impressions']} imp)")

    if not any([opportunities['striking_distance'], opportunities['low_ctr'], opportunities['quick_wins']]):
        print("  No opportunities found yet - need more indexed pages and data.")

    print("\n" + "="*60)

    # Save report
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_file = f"{REPORT_DIR}/gsc_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"📁 Report saved to: {report_file}")

    return report


def main():
    parser = argparse.ArgumentParser(description='GSC Tracking for thegreenleaf.com')
    parser.add_argument('--indexed-only', action='store_true', help='Only show indexed pages')
    parser.add_argument('--opportunities', action='store_true', help='Focus on opportunities')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--days', type=int, default=28, help='Days of data to fetch (default: 28)')
    args = parser.parse_args()

    print("🔍 Connecting to Google Search Console...")
    service = get_gsc_service()

    if not service:
        return

    print("📚 Loading local articles...")
    local_articles = get_local_articles()
    print(f"   Found {len(local_articles)} articles")

    print("📊 Fetching performance data...")
    performance_data = get_performance_data(service, args.days)
    print(f"   Got data for {len(performance_data)} URLs")

    print("🔎 Fetching keyword data...")
    keyword_data = get_keyword_data(service, args.days)
    print(f"   Got {len(keyword_data)} keyword entries")

    print("📈 Analyzing...")
    indexed, not_indexed = analyze_indexing(local_articles, performance_data)
    opportunities = find_opportunities(keyword_data)

    if args.indexed_only:
        not_indexed = []

    generate_report(indexed, not_indexed, opportunities, args.json)


if __name__ == '__main__':
    main()
