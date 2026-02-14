"""
Automated Amazon Affiliate Link System
Detects product opportunities in lawn care content and inserts affiliate links.
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Amazon Affiliate Tag
AFFILIATE_TAG = os.getenv('AMAZON_AFFILIATE_TAG', 'amazonlinkp00-20')

# FTC Disclosure
AFFILIATE_DISCLOSURE = """
*This article contains affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you.*
""".strip()


def load_product_database():
    """Load the curated product database."""
    db_path = Path(__file__).parent / "products" / "lawn_care_products.json"
    with open(db_path, 'r') as f:
        return json.load(f)


def build_affiliate_url(search_term: str, asin: str = None) -> str:
    """
    Build Amazon affiliate link.

    Args:
        search_term: Product search query
        asin: Optional direct product ASIN for higher conversion

    Returns:
        Amazon URL with affiliate tag
    """
    # Always use search URLs for now - more reliable and still earns commission
    # User gets commission on anything they buy within 24 hours after clicking
    encoded = search_term.replace(' ', '+')
    return f"https://www.amazon.com/s?k={encoded}&tag={AFFILIATE_TAG}"


def find_product_opportunities(content: str, product_db: dict, max_links: int = 5) -> List[Dict]:
    """
    Scan content for product mention opportunities.

    Args:
        content: Article markdown content
        product_db: Product database
        max_links: Maximum affiliate links per article (default 5)

    Returns:
        List of product opportunities with metadata
    """
    opportunities = []
    content_lower = content.lower()

    for category in product_db['products']:
        for product in category['items']:
            # Check if any product keywords appear in content
            for keyword in product['keywords']:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, content_lower, re.IGNORECASE):
                    # Found a match!
                    opportunities.append({
                        'product_name': product['name'],
                        'keyword': keyword,
                        'amazon_search': product['amazon_search'],
                        'asin': product.get('asin'),
                        'category': category['category'],
                        'best_for': product.get('best_for', ''),
                        'price_range': product.get('price_range', '')
                    })
                    break  # Only add product once even if multiple keywords match

    # Sort by keyword length (longer = more specific = better match)
    opportunities.sort(key=lambda x: len(x['keyword']), reverse=True)

    # Return top opportunities up to max_links
    return opportunities[:max_links]


def insert_affiliate_links(content: str, opportunities: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Insert affiliate links into content naturally.

    Args:
        content: Article markdown content (body only, no frontmatter)
        opportunities: List of product opportunities

    Returns:
        Tuple of (modified content, list of inserted links metadata)
    """
    inserted_links = []
    modified_content = content

    # Find where Sources section starts (don't insert links there)
    sources_start = len(content)
    sources_match = re.search(r'^## Sources\s*$', content, re.MULTILINE)
    if sources_match:
        sources_start = sources_match.start()

    for opp in opportunities:
        keyword = opp['keyword']

        # Build affiliate URL (prefer ASIN if available)
        url = build_affiliate_url(
            opp['amazon_search'],
            asin=opp.get('asin')
        )

        # Find first occurrence of keyword (case-insensitive but preserve original case)
        pattern = r'\b(' + re.escape(keyword) + r')\b'
        match = re.search(pattern, modified_content, re.IGNORECASE)

        if match:
            original_text = match.group(1)
            start, end = match.span()

            # Skip if in Sources section
            if start >= sources_start:
                continue

            # Skip if in H1 heading (first line starting with #)
            line_start = modified_content.rfind('\n', 0, start) + 1
            line = modified_content[line_start:start]
            if line.strip().startswith('# '):
                continue

            # Check if already linked (avoid double-linking)
            # Look back to see if we're already inside a markdown link
            preceding_text = modified_content[max(0, start-50):start]
            if '[' in preceding_text and ']' not in preceding_text:
                continue  # Already inside a link, skip

            # Create markdown link
            linked_text = f'[{original_text}]({url})'

            # Replace in content
            modified_content = modified_content[:start] + linked_text + modified_content[end:]

            # Adjust sources_start since we added characters
            sources_start += len(linked_text) - len(original_text)

            # Track inserted link
            inserted_links.append({
                'keyword': keyword,
                'product': opp['product_name'],
                'url': url,
                'category': opp['category']
            })

    return modified_content, inserted_links


def add_affiliate_disclosure(content: str, has_links: bool = True) -> str:
    """
    Add FTC-required affiliate disclosure to article.

    Args:
        content: Article content
        has_links: Whether article contains affiliate links

    Returns:
        Content with disclosure added
    """
    if not has_links:
        return content

    # Check if disclosure already exists to prevent duplicates
    if AFFILIATE_DISCLOSURE in content or "This article contains affiliate links" in content:
        return content

    # Add disclosure at the top, right after the first H1
    lines = content.split('\n')
    new_lines = []
    h1_found = False

    for line in lines:
        new_lines.append(line)

        # Insert disclosure after first H1 and its following blank line
        if not h1_found and line.startswith('# '):
            h1_found = True
            new_lines.append('')
            new_lines.append(AFFILIATE_DISCLOSURE)

    return '\n'.join(new_lines)


def process_article_for_affiliates(content: str, max_links: int = 5) -> Dict:
    """
    Complete affiliate processing pipeline for an article.

    Args:
        content: Article markdown content
        max_links: Maximum links to insert

    Returns:
        Dict with processed content and metadata
    """
    # Load product database
    product_db = load_product_database()

    # Split frontmatter from body - ONLY process body content
    # This prevents inserting links into YAML title, tags, youtube insights, etc.
    parts = content.split('---', 2)
    if len(parts) >= 3:
        frontmatter = parts[0] + '---' + parts[1] + '---'
        body = parts[2]
    else:
        frontmatter = ''
        body = content

    # Find product opportunities (only in body)
    opportunities = find_product_opportunities(body, product_db, max_links)

    # Insert links (only in body)
    modified_body, inserted_links = insert_affiliate_links(body, opportunities)

    # Add disclosure if we inserted any links
    if inserted_links:
        modified_body = add_affiliate_disclosure(modified_body, True)

    # Recombine frontmatter + modified body
    modified_content = frontmatter + modified_body

    return {
        'content': modified_content,
        'affiliate_links': inserted_links,
        'link_count': len(inserted_links),
        'has_affiliates': len(inserted_links) > 0
    }


def generate_affiliate_metadata(inserted_links: List[Dict]) -> Dict:
    """
    Generate frontmatter metadata for tracking affiliate links.

    Args:
        inserted_links: List of inserted link metadata

    Returns:
        Dict suitable for article frontmatter
    """
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


# Example usage
if __name__ == "__main__":
    # Test with sample content
    sample_content = """# How to Aerate Your Lawn

Lawn aeration is essential for healthy grass growth. Using a core aerator helps improve soil drainage and oxygen flow to grass roots.

## Tools You'll Need

For aerating, you'll need a manual aerator or spike aerator shoes for small lawns. Larger properties benefit from a powered aerator.

## Best Practices

Apply lawn fertilizer after aeration for better nutrient absorption. Use a broadcast spreader for even application.
"""

    result = process_article_for_affiliates(sample_content, max_links=5)

    print("=" * 60)
    print("AFFILIATE LINK TEST RESULTS")
    print("=" * 60)
    print(f"\nInserted {result['link_count']} affiliate links:")
    for link in result['affiliate_links']:
        print(f"  • {link['keyword']} → {link['product']}")
        print(f"    {link['url']}")

    print("\n" + "=" * 60)
    print("MODIFIED CONTENT:")
    print("=" * 60)
    print(result['content'])
