"""Amazon affiliate link insertion for generated articles."""
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Amazon Affiliate Tag — MUST come from env / GitHub Actions secret.
# Do not hardcode the store tag in source. Set AMAZON_AFFILIATE_TAG in:
#   - local .env
#   - GitHub Actions secret AMAZON_AFFILIATE_TAG (e.g. thegreenleaf2-20)
# Empty/missing tag => affiliate insertion is skipped (no broken/untagged links).
AFFILIATE_TAG = (os.getenv('AMAZON_AFFILIATE_TAG') or '').strip()

# FTC Disclosure
AFFILIATE_DISCLOSURE = """
*This article contains affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you.*
""".strip()


def load_product_database():
    db_path = Path(__file__).parent / "products" / "cannabis_products.json"
    with open(db_path, 'r') as f:
        return json.load(f)


def build_affiliate_url(search_term: str, asin: str = None) -> str:
    if not AFFILIATE_TAG:
        return ''

    # Prefer ASIN deep links when available (higher conversion); else search URL.
    # Commission still applies to anything purchased within the cookie window.
    if asin:
        return f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"

    encoded = search_term.replace(' ', '+')
    return f"https://www.amazon.com/s?k={encoded}&tag={AFFILIATE_TAG}"


def find_product_opportunities(content: str, product_db: dict, max_links: int = 5) -> List[Dict]:
    opportunities = []
    content_lower = content.lower()

    for category in product_db['products']:
        for product in category['items']:
            for keyword in product['keywords']:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, content_lower, re.IGNORECASE):
                    opportunities.append({
                        'product_name': product['name'],
                        'keyword': keyword,
                        'amazon_search': product['amazon_search'],
                        'asin': product.get('asin'),
                        'category': category['category'],
                        'best_for': product.get('best_for', ''),
                        'price_range': product.get('price_range', '')
                    })
                    break

    opportunities.sort(key=lambda x: len(x['keyword']), reverse=True)
    return opportunities[:max_links]


def insert_affiliate_links(content: str, opportunities: List[Dict]) -> Tuple[str, List[Dict]]:
    inserted_links = []
    modified_content = content

    sources_start = len(content)
    sources_match = re.search(r'^## Sources\s*$', content, re.MULTILINE)
    if sources_match:
        sources_start = sources_match.start()

    for opp in opportunities:
        keyword = opp['keyword']
        url = build_affiliate_url(opp['amazon_search'], asin=opp.get('asin'))
        if not url:
            continue

        pattern = r'\b(' + re.escape(keyword) + r')\b'
        match = re.search(pattern, modified_content, re.IGNORECASE)

        if match:
            original_text = match.group(1)
            start, end = match.span()

            if start >= sources_start:
                continue

            line_start = modified_content.rfind('\n', 0, start) + 1
            line = modified_content[line_start:start]
            if line.strip().startswith('# '):
                continue

            preceding_text = modified_content[max(0, start-50):start]
            if '[' in preceding_text and ']' not in preceding_text:
                continue

            linked_text = f'[{original_text}]({url})'
            modified_content = modified_content[:start] + linked_text + modified_content[end:]
            sources_start += len(linked_text) - len(original_text)

            inserted_links.append({
                'keyword': keyword,
                'product': opp['product_name'],
                'url': url,
                'category': opp['category']
            })

    return modified_content, inserted_links


def add_affiliate_disclosure(content: str, has_links: bool = True) -> str:
    if not has_links:
        return content

    if AFFILIATE_DISCLOSURE in content or "This article contains affiliate links" in content:
        return content

    lines = content.split('\n')
    new_lines = []
    h1_found = False

    for line in lines:
        new_lines.append(line)
        if not h1_found and line.startswith('# '):
            h1_found = True
            new_lines.append('')
            new_lines.append(AFFILIATE_DISCLOSURE)

    return '\n'.join(new_lines)


def process_article_for_affiliates(content: str, max_links: int = 5) -> Dict:
    empty = {
        'content': content,
        'affiliate_links': [],
        'link_count': 0,
        'has_affiliates': False,
    }

    if not AFFILIATE_TAG:
        print("   ⚠️  AMAZON_AFFILIATE_TAG not set — skipping affiliate insertion.")
        print("       Set GitHub Actions secret AMAZON_AFFILIATE_TAG (e.g. thegreenleaf2-20).")
        return empty

    product_db = load_product_database()

    # Only treat leading YAML as frontmatter. Splitting on every '---' breaks
    # body-only markdown that contains horizontal rules.
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[0] + '---' + parts[1] + '---'
            body = parts[2]
        else:
            frontmatter = ''
            body = content
    else:
        frontmatter = ''
        body = content

    opportunities = find_product_opportunities(body, product_db, max_links)
    modified_body, inserted_links = insert_affiliate_links(body, opportunities)

    if inserted_links:
        modified_body = add_affiliate_disclosure(modified_body, True)

    return {
        'content': frontmatter + modified_body,
        'affiliate_links': inserted_links,
        'link_count': len(inserted_links),
        'has_affiliates': len(inserted_links) > 0
    }


def generate_affiliate_metadata(inserted_links: List[Dict]) -> Dict:
    if not inserted_links:
        return {}

    return {
        'has_affiliate_links': True,
        'affiliate_count': len(inserted_links),
        'affiliate_links': [
            {
                'product': link['product'],
                'keyword': link['keyword'],
                'category': link['category'],
                'url': link['url']
            }
            for link in inserted_links
        ]
    }
