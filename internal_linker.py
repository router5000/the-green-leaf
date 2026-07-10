"""
Internal Linking System for SEO
Automatically inserts internal links between related articles to improve SEO and user experience.
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


# Directories
POSTS_DIR = Path(__file__).parent / "site" / "content" / "posts"
SITE_URL = "https://strainreport.com"


def load_article_index() -> List[Dict]:
    """
    Load all published articles and build a searchable index.

    Returns:
        List of article metadata dicts with keywords, title, slug, etc.
    """
    articles = []

    if not POSTS_DIR.exists():
        return articles

    for md_file in POSTS_DIR.glob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')

            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter and frontmatter.get('status') == 'published':
                        # Build search terms from title, keyword, tags
                        search_terms = set()

                        # Primary keyword
                        keyword = frontmatter.get('keyword', '')
                        if keyword:
                            search_terms.add(keyword.lower().strip('"'))

                        # Title words (excluding common words)
                        title = frontmatter.get('title', '')
                        title_words = extract_key_phrases(title)
                        search_terms.update(title_words)

                        # Tags
                        tags = frontmatter.get('tags', [])
                        if isinstance(tags, list):
                            search_terms.update(t.lower() for t in tags)

                        # Slug-based terms
                        slug = frontmatter.get('slug', md_file.stem)
                        slug_terms = slug.replace('-', ' ').split()
                        search_terms.update(t.lower() for t in slug_terms if len(t) > 3)

                        articles.append({
                            'slug': slug,
                            'title': title,
                            'keyword': keyword,
                            'search_terms': list(search_terms),
                            'season': frontmatter.get('season', 'evergreen'),
                            'tags': tags,
                            'file_path': str(md_file)
                        })
        except Exception as e:
            print(f"Warning: Could not parse {md_file.name}: {e}")

    return articles


def extract_key_phrases(text: str) -> List[str]:
    """
    Extract meaningful phrases from text for matching.

    Args:
        text: Input text (title, etc.)

    Returns:
        List of lowercase key phrases
    """
    # Common words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
        'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'how',
        'when', 'where', 'why', 'your', 'you', 'my', 'our', 'their', 'its',
        'best', 'top', 'complete', 'ultimate', 'guide', 'tips', 'expert'
    }

    # Terms too generic for anchor text (would create poor UX)
    generic_terms = {
        'cannabis', 'grass', 'yard', 'cannabis', 'your cannabis', 'the cannabis',
        'small', 'large', 'keep', 'to keep', 'for small'
    }

    phrases = []
    text_lower = text.lower()

    # Remove punctuation except hyphens
    text_clean = re.sub(r'[^\w\s-]', '', text_lower)
    words = text_clean.split()

    # Two-word phrases (bigrams) - prefer these over single words
    for i in range(len(words) - 1):
        if words[i] not in stop_words or words[i+1] not in stop_words:
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) > 8 and bigram not in generic_terms:
                phrases.append(bigram)

    # Three-word phrases for specific patterns
    for i in range(len(words) - 2):
        trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
        # Keep trigrams with cannabis-specific terms
        if any(term in trigram for term in ['cannabis', 'grass', 'mow', 'water', 'fertil', 'weed', 'aerat', 'dethatch', 'overseed']):
            if trigram not in generic_terms:
                phrases.append(trigram)

    # Single meaningful words only if very specific (compound terms)
    specific_singles = ['crabgrass', 'dethatch', 'dethatching', 'aeration', 'aerating', 'overseeding',
                        'fertilizer', 'fungicide', 'herbicide', 'scalping', 'winterize', 'winterizing']
    for word in words:
        if word in specific_singles or (len(word) > 8 and word not in stop_words):
            phrases.append(word)

    return phrases


def find_internal_link_opportunities(
    content: str,
    current_slug: str,
    article_index: List[Dict],
    max_links: int = 5
) -> List[Dict]:
    """
    Find opportunities to link to other articles.

    Args:
        content: Article markdown content (body only)
        current_slug: Slug of current article (to avoid self-linking)
        article_index: List of all article metadata
        max_links: Maximum internal links to insert

    Returns:
        List of link opportunities with position info
    """
    # Terms too generic for anchor text
    generic_terms = {
        'cannabis', 'grass', 'yard', 'cannabis', 'your cannabis', 'the cannabis',
        'small', 'large', 'keep', 'to keep', 'for small', 'mower',
        'spring', 'summer', 'fall', 'winter', 'water', 'watering',
        'mowing', 'before', 'after', 'without', 'weather', 'timing',
        'season', 'seasonal', 'control', 'techniques', 'preparation',
        'Spring cannabis', 'season grass', 'warm season'
    }

    opportunities = []
    content_lower = content.lower()
    used_slugs = set()  # Track which articles we've already linked to

    # Sort articles by search term length (prefer longer, more specific matches)
    for article in article_index:
        if article['slug'] == current_slug:
            continue  # Don't link to self

        if article['slug'] in used_slugs:
            continue  # Already linked to this article

        # Check each search term
        for term in sorted(article['search_terms'], key=len, reverse=True):
            if len(term) < 8:
                continue  # Skip short terms - need meaningful anchor text

            if term.lower() in generic_terms:
                continue  # Skip generic terms

            # Look for whole-word match
            pattern = r'\b' + re.escape(term) + r'\b'
            match = re.search(pattern, content_lower)

            if match:
                # Check context - avoid matching in headings, links, etc.
                start = match.start()

                # Find the actual position in original content
                original_match = re.search(pattern, content, re.IGNORECASE)
                if original_match:
                    opportunities.append({
                        'slug': article['slug'],
                        'title': article['title'],
                        'matched_term': term,
                        'original_text': original_match.group(),
                        'position': original_match.start(),
                        'term_length': len(term)
                    })
                    used_slugs.add(article['slug'])
                    break  # Only one link per target article

        if len(opportunities) >= max_links:
            break

    # Sort by position so we process front-to-back
    opportunities.sort(key=lambda x: x['position'])

    return opportunities[:max_links]


def insert_internal_links(
    content: str,
    opportunities: List[Dict]
) -> Tuple[str, List[Dict]]:
    """
    Insert internal links into content.

    Args:
        content: Article markdown content
        opportunities: List of link opportunities

    Returns:
        Tuple of (modified content, list of inserted links)
    """
    inserted = []
    modified = content
    offset = 0  # Track character offset as we modify

    # Find sections to avoid (frontmatter, sources, headings, existing links)
    sources_match = re.search(r'^## Sources\s*$', content, re.MULTILINE)
    sources_start = sources_match.start() if sources_match else len(content)

    for opp in opportunities:
        # Find the term in modified content (accounting for offset)
        pattern = r'\b(' + re.escape(opp['matched_term']) + r')\b'

        # Search from current position onwards
        search_start = 0
        match = None

        for m in re.finditer(pattern, modified, re.IGNORECASE):
            pos = m.start()

            # Skip if in sources section
            if pos >= sources_start + offset:
                continue

            # Skip if inside a markdown link [...](...) or ![...]
            preceding = modified[max(0, pos-100):pos]
            if '[' in preceding:
                # Check if we're between [ and ]
                last_open = preceding.rfind('[')
                last_close = preceding.rfind(']')
                if last_open > last_close:
                    continue  # Inside link text

            # Skip if in a heading line
            line_start = modified.rfind('\n', 0, pos) + 1
            line = modified[line_start:pos]
            if line.strip().startswith('#'):
                continue

            # Skip if in image alt text
            if '![' in modified[max(0, pos-50):pos]:
                last_img = modified.rfind('![', 0, pos)
                last_close = modified.rfind(')', 0, pos)
                if last_img > last_close:
                    continue

            match = m
            break

        if match:
            original_text = match.group(1)
            start = match.start()
            end = match.end()

            # Create internal link
            url = f"/articles/{opp['slug']}"
            link = f'[{original_text}]({url})'

            # Replace
            modified = modified[:start] + link + modified[end:]

            # Update sources position
            sources_start += len(link) - len(original_text)

            inserted.append({
                'target_slug': opp['slug'],
                'target_title': opp['title'],
                'anchor_text': original_text,
                'url': url
            })

    return modified, inserted


def process_article_for_internal_links(
    file_path: str,
    article_index: List[Dict],
    max_links: int = 5,
    dry_run: bool = False
) -> Dict:
    """
    Process a single article and add internal links.

    Args:
        file_path: Path to the markdown file
        article_index: Index of all articles
        max_links: Maximum links to insert
        dry_run: If True, don't modify the file

    Returns:
        Dict with results
    """
    path = Path(file_path)
    content = path.read_text(encoding='utf-8')

    # Parse to get slug
    slug = path.stem
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            slug = frontmatter.get('slug', slug)
            body = parts[2]
            frontmatter_text = parts[0] + '---' + parts[1] + '---'
        else:
            body = content
            frontmatter_text = ''
    else:
        body = content
        frontmatter_text = ''

    # Find opportunities
    opportunities = find_internal_link_opportunities(body, slug, article_index, max_links)

    if not opportunities:
        return {
            'file': str(path),
            'slug': slug,
            'links_added': 0,
            'links': []
        }

    # Insert links
    modified_body, inserted = insert_internal_links(body, opportunities)

    if inserted and not dry_run:
        # Write back
        modified_content = frontmatter_text + modified_body
        path.write_text(modified_content, encoding='utf-8')

    return {
        'file': str(path),
        'slug': slug,
        'links_added': len(inserted),
        'links': inserted
    }


def process_all_articles(
    max_links_per_article: int = 5,
    dry_run: bool = False
) -> Dict:
    """
    Process all published articles and add internal links.

    Args:
        max_links_per_article: Max links per article
        dry_run: If True, don't modify files

    Returns:
        Summary of processing
    """
    # Build index
    article_index = load_article_index()
    print(f"Loaded {len(article_index)} published articles")

    results = []
    total_links = 0

    for article in article_index:
        result = process_article_for_internal_links(
            article['file_path'],
            article_index,
            max_links_per_article,
            dry_run
        )
        results.append(result)
        total_links += result['links_added']

        if result['links_added'] > 0:
            print(f"\n{article['slug']}: +{result['links_added']} internal links")
            for link in result['links']:
                print(f"  → {link['anchor_text']} → {link['target_slug']}")

    return {
        'articles_processed': len(results),
        'total_links_added': total_links,
        'results': results
    }


def add_internal_links_to_new_article(content: str, slug: str) -> Tuple[str, List[Dict]]:
    """
    Add internal links to a newly generated article.
    Called from content_generator.py during article creation.

    Args:
        content: Full article content with frontmatter
        slug: Article slug

    Returns:
        Tuple of (modified content, list of added links)
    """
    # Build index from existing articles
    article_index = load_article_index()

    # Parse content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[0] + '---' + parts[1] + '---'
            body = parts[2]
        else:
            return content, []
    else:
        return content, []

    # Find and insert links
    opportunities = find_internal_link_opportunities(body, slug, article_index, max_links=5)

    if not opportunities:
        return content, []

    modified_body, inserted = insert_internal_links(body, opportunities)

    return frontmatter_text + modified_body, inserted


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add internal links between articles")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--max-links", type=int, default=5, help="Maximum links per article (default: 5)")
    parser.add_argument("--article", type=str, help="Process single article by slug or path")

    args = parser.parse_args()

    print("=" * 60)
    print("INTERNAL LINKING SYSTEM")
    print("=" * 60)

    if args.article:
        # Process single article
        article_index = load_article_index()

        # Find article by slug or path
        target_path = None
        for article in article_index:
            if args.article == article['slug'] or args.article in article['file_path']:
                target_path = article['file_path']
                break

        if not target_path:
            # Try as direct path
            if Path(args.article).exists():
                target_path = args.article
            else:
                print(f"Article not found: {args.article}")
                exit(1)

        result = process_article_for_internal_links(
            target_path,
            article_index,
            args.max_links,
            args.dry_run
        )

        print(f"\nProcessed: {result['slug']}")
        print(f"Links added: {result['links_added']}")
        for link in result['links']:
            print(f"  → {link['anchor_text']} → {link['target_slug']}")
    else:
        # Process all articles
        summary = process_all_articles(
            max_links_per_article=args.max_links,
            dry_run=args.dry_run
        )

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Articles processed: {summary['articles_processed']}")
        print(f"Total internal links added: {summary['total_links_added']}")

        if args.dry_run:
            print("\n(Dry run - no files were modified)")
