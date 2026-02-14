"""
SEO Validation Module
Automated checks for common SEO issues in generated content.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
import yaml

# Try to import anthropic for AI-powered alt text
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# ============================================================================
# LINK VALIDATION
# ============================================================================

def validate_markdown_links(content: str) -> Dict:
    """
    Validate all markdown links in content for common issues.

    Returns:
        Dict with validation results and issues found
    """
    issues = []

    # Pattern to find all markdown links [text](url)
    link_pattern = r'\[([^\]]*)\]\(([^)]*)\)'

    # Check for nested links - [text [nested](url)](outer-url)
    # But exclude citation links like [[1]](#user-content-fn-1) which are valid
    nested_pattern = r'\[([^\]]*\[[^\]]*\][^\]]*)\]\([^)]*\)'
    nested_matches = re.findall(nested_pattern, content)
    for match in nested_matches:
        # Skip citation links [[1]], [[2]], etc. - these are valid footnote references
        if re.match(r'^\[\d+\]$', match.strip()):
            continue
        # Skip if match is just a number in brackets (citation)
        if re.match(r'^\s*\[\d+\]\s*$', match):
            continue
        issues.append({
            'type': 'nested_link',
            'severity': 'critical',
            'description': f'Nested link detected in: [{match[:50]}...]',
            'match': match
        })

    # Check for broken link syntax - unbalanced brackets
    # Count opening and closing brackets
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    if open_brackets != close_brackets:
        issues.append({
            'type': 'unbalanced_brackets',
            'severity': 'warning',
            'description': f'Unbalanced brackets: {open_brackets} "[" vs {close_brackets} "]"'
        })

    # Check for empty links
    empty_link_pattern = r'\[\s*\]\([^)]+\)'
    empty_links = re.findall(empty_link_pattern, content)
    for link in empty_links:
        issues.append({
            'type': 'empty_link_text',
            'severity': 'warning',
            'description': f'Empty link text: {link}'
        })

    # Check for links with empty URLs
    empty_url_pattern = r'\[[^\]]+\]\(\s*\)'
    empty_urls = re.findall(empty_url_pattern, content)
    for link in empty_urls:
        issues.append({
            'type': 'empty_url',
            'severity': 'critical',
            'description': f'Empty URL: {link}'
        })

    # Check for duplicate disclosure
    disclosure_pattern = r'\*This article contains affiliate links[^*]*\*'
    disclosures = re.findall(disclosure_pattern, content, re.IGNORECASE)
    if len(disclosures) > 1:
        issues.append({
            'type': 'duplicate_disclosure',
            'severity': 'warning',
            'description': f'Found {len(disclosures)} affiliate disclosures (should be 1)'
        })

    return {
        'valid': len([i for i in issues if i['severity'] == 'critical']) == 0,
        'issues': issues,
        'issue_count': len(issues),
        'critical_count': len([i for i in issues if i['severity'] == 'critical'])
    }


def fix_nested_links(content: str) -> Tuple[str, int]:
    """
    Attempt to fix nested markdown links.

    Returns:
        Tuple of (fixed_content, number_of_fixes)
    """
    fixes = 0

    # Pattern to find nested links like [text [inner](url1)](url2)
    # We want to keep the outer link structure
    nested_pattern = r'\[([^\[\]]*)\[([^\]]+)\]\([^)]+\)([^\[\]]*)\]\(([^)]+)\)'

    def fix_nested(match):
        nonlocal fixes
        before_text = match.group(1)
        inner_text = match.group(2)
        after_text = match.group(3)
        outer_url = match.group(4)
        fixes += 1
        # Combine text and use outer URL
        combined_text = (before_text + inner_text + after_text).strip()
        return f'[{combined_text}]({outer_url})'

    fixed_content = re.sub(nested_pattern, fix_nested, content)

    # Handle deeply nested (3+ levels) by iterating
    while re.search(nested_pattern, fixed_content):
        fixed_content = re.sub(nested_pattern, fix_nested, fixed_content)

    return fixed_content, fixes


def fix_duplicate_disclosures(content: str) -> Tuple[str, int]:
    """
    Remove duplicate affiliate disclosures, keeping only the first one.

    Returns:
        Tuple of (fixed_content, number_of_removals)
    """
    disclosure_pattern = r'\*This article contains affiliate links[^*]*\*'
    matches = list(re.finditer(disclosure_pattern, content, re.IGNORECASE))

    if len(matches) <= 1:
        return content, 0

    # Keep the first, remove the rest (in reverse order to maintain positions)
    removals = 0
    for match in reversed(matches[1:]):
        # Remove the disclosure and any surrounding blank lines
        start = match.start()
        end = match.end()

        # Check for preceding newline
        if start > 0 and content[start-1] == '\n':
            start -= 1
        # Check for following newline
        if end < len(content) and content[end] == '\n':
            end += 1

        content = content[:start] + content[end:]
        removals += 1

    return content, removals


# ============================================================================
# ALT TEXT GENERATION
# ============================================================================

def generate_smart_alt_text(keyword: str, title: str, image_type: str = "hero",
                            image_prompt: str = None) -> str:
    """
    Generate SEO-friendly, descriptive alt text for images.

    Uses AI when available, falls back to enhanced rule-based generation.

    Args:
        keyword: Target keyword for the article
        title: Article title
        image_type: "hero" or "section"
        image_prompt: Optional prompt used to generate the image

    Returns:
        Descriptive alt text under 125 characters
    """
    # Try AI-powered generation first
    if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
        try:
            return _generate_alt_text_with_ai(keyword, title, image_type, image_prompt)
        except Exception as e:
            print(f"   AI alt text generation failed: {e}, using fallback")

    # Enhanced rule-based fallback
    return _generate_alt_text_rules(keyword, title, image_type)


def _generate_alt_text_with_ai(keyword: str, title: str, image_type: str,
                                image_prompt: str = None) -> str:
    """Generate alt text using Claude."""
    client = Anthropic()

    context = f"Image type: {image_type}\nKeyword: {keyword}\nArticle: {title}"
    if image_prompt:
        context += f"\nImage shows: {image_prompt}"

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": f"""Generate SEO-friendly alt text for a lawn care article image.

{context}

Requirements:
- Be specific and descriptive (what does the image show?)
- Naturally include the keyword when relevant
- Maximum 120 characters
- No quotes or special formatting
- Focus on what a viewer would see

Return ONLY the alt text, nothing else."""
        }]
    )

    alt_text = response.content[0].text.strip().strip('"\'')
    return alt_text[:125]


def _generate_alt_text_rules(keyword: str, title: str, image_type: str) -> str:
    """Enhanced rule-based alt text generation."""
    keyword_lower = keyword.lower()

    # Comprehensive keyword patterns for lawn care
    patterns = {
        # Aeration
        'aerat': 'Lawn aerator creating soil plugs to improve grass root health and drainage',
        'core aerat': 'Core aerator machine removing soil plugs from compacted lawn',

        # Mowing
        'mow': 'Freshly mowed lawn showing professional striping pattern',
        'cutting height': 'Grass blade at optimal cutting height for healthy growth',
        'scalp': 'Lawn showing recovery after spring scalping treatment',

        # Watering
        'water': 'Sprinkler system watering healthy green lawn at optimal time',
        'irrigat': 'Underground irrigation system providing even lawn coverage',
        'drought': 'Drought-stressed lawn showing signs of water deficiency',

        # Fertilizing
        'fertiliz': 'Broadcast spreader applying granular fertilizer to lawn',
        'granular': 'Granular lawn fertilizer pellets on grass surface',
        'liquid': 'Liquid fertilizer being sprayed on lawn foliage',

        # Weeds
        'weed': 'Healthy weed-free lawn with dense grass coverage',
        'crabgrass': 'Crabgrass weed identified in lawn before treatment',
        'dandelion': 'Dandelion weeds being removed from lawn',

        # Seeding
        'seed': 'New grass seedlings emerging from overseeded lawn',
        'overseed': 'Lawn being overseeded with grass seed for thicker coverage',
        'germina': 'Grass seeds germinating in prepared soil bed',

        # Thatch
        'thatch': 'Thatch layer being removed from lawn with dethatching rake',
        'dethatch': 'Power dethatcher removing dead material from lawn surface',

        # Soil
        'soil': 'Healthy lawn soil showing good structure and root development',
        'ph': 'Soil pH test kit measuring lawn soil acidity levels',
        'compact': 'Compacted lawn soil before aeration treatment',

        # Pests
        'grub': 'White grubs in lawn soil causing grass damage',
        'pest': 'Lawn pest damage visible in brown patch area',
        'fungus': 'Fungal disease symptoms on grass blades',
        'brown patch': 'Brown patch fungus creating circular dead spots in lawn',

        # Seasonal
        'spring': 'Lawn emerging from winter dormancy in early spring',
        'summer': 'Lush green lawn thriving in summer conditions',
        'fall': 'Autumn lawn preparation with fallen leaves on grass',
        'winter': 'Dormant lawn covered in light frost',

        # Equipment
        'mower': 'Lawn mower cutting grass at proper height setting',
        'spreader': 'Fertilizer spreader distributing product evenly on lawn',
        'robot': 'Robotic lawn mower navigating residential yard',

        # Problems
        'patch': 'Patchy lawn showing bare spots needing repair',
        'bare spot': 'Bare soil patch in lawn prepared for reseeding',
        'yellow': 'Yellowing grass indicating nutrient deficiency',
        'brown': 'Brown lawn area showing signs of stress or dormancy',
        'drain': 'Lawn drainage problem with standing water on grass',
    }

    # Find best matching pattern
    for pattern, alt_text in patterns.items():
        if pattern in keyword_lower:
            return alt_text[:125]

    # Default based on image type
    if image_type == "hero":
        # Extract main action from keyword for hero
        return f"Professional lawn care: {keyword} - healthy residential grass"[:125]
    else:
        return f"Detailed view of {keyword} technique on green lawn"[:125]


# ============================================================================
# KEYWORD CANNIBALIZATION DETECTION
# ============================================================================

def load_existing_keywords(posts_dir: str = "site/content/posts") -> List[Dict]:
    """
    Load keywords from all existing published articles.

    Returns:
        List of dicts with slug, keyword, title, tags
    """
    articles = []
    posts_path = Path(posts_dir)

    if not posts_path.exists():
        return articles

    for md_file in posts_path.glob("*.md"):
        try:
            content = md_file.read_text()
            # Extract frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter and frontmatter.get('status') == 'published':
                        articles.append({
                            'slug': frontmatter.get('slug', md_file.stem),
                            'keyword': frontmatter.get('keyword', ''),
                            'title': frontmatter.get('title', ''),
                            'tags': frontmatter.get('tags', []),
                            'file': str(md_file)
                        })
        except Exception as e:
            print(f"Error loading {md_file}: {e}")
            continue

    return articles


def normalize_keyword(keyword: str) -> set:
    """
    Normalize keyword into a set of stemmed words for comparison.
    """
    # Common words to remove
    stop_words = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
        'for', 'on', 'with', 'at', 'by', 'from', 'as', 'or', 'and', 'but',
        'if', 'then', 'so', 'than', 'that', 'this', 'what', 'when', 'where',
        'why', 'how', 'which', 'who', 'whom', 'whose', 'i', 'my', 'me', 'you',
        'your', 'we', 'our', 'they', 'their', 'it', 'its'
    }

    # Normalize and tokenize
    words = re.findall(r'\b[a-z]+\b', keyword.lower())

    # Remove stop words and very short words
    meaningful_words = {w for w in words if w not in stop_words and len(w) > 2}

    return meaningful_words


def calculate_keyword_similarity(keyword1: str, keyword2: str) -> float:
    """
    Calculate similarity between two keywords.

    Returns:
        Float between 0 and 1 (1 = identical)
    """
    words1 = normalize_keyword(keyword1)
    words2 = normalize_keyword(keyword2)

    if not words1 or not words2:
        return 0.0

    # Jaccard similarity
    intersection = words1 & words2
    union = words1 | words2

    jaccard = len(intersection) / len(union) if union else 0

    # Also consider sequence similarity for similar phrasing
    sequence_sim = SequenceMatcher(None, keyword1.lower(), keyword2.lower()).ratio()

    # Weight both measures
    return (jaccard * 0.6) + (sequence_sim * 0.4)


def detect_cannibalization(new_keyword: str, threshold: float = 0.6,
                           posts_dir: str = "site/content/posts") -> List[Dict]:
    """
    Detect if a new keyword might cannibalize existing articles.

    Args:
        new_keyword: The keyword for the new article
        threshold: Similarity threshold (0-1) to flag as potential cannibalization
        posts_dir: Path to posts directory

    Returns:
        List of potentially conflicting articles with similarity scores
    """
    existing = load_existing_keywords(posts_dir)
    conflicts = []

    for article in existing:
        existing_keyword = article.get('keyword', '')
        if not existing_keyword:
            continue

        similarity = calculate_keyword_similarity(new_keyword, existing_keyword)

        if similarity >= threshold:
            conflicts.append({
                'slug': article['slug'],
                'keyword': existing_keyword,
                'title': article['title'],
                'similarity': round(similarity, 2),
                'file': article['file']
            })

    # Sort by similarity (highest first)
    conflicts.sort(key=lambda x: x['similarity'], reverse=True)

    return conflicts


def get_cannibalization_recommendation(conflicts: List[Dict]) -> str:
    """
    Generate a recommendation based on cannibalization detection results.
    """
    if not conflicts:
        return "✅ No keyword cannibalization detected. Safe to proceed."

    high_similarity = [c for c in conflicts if c['similarity'] >= 0.8]
    medium_similarity = [c for c in conflicts if 0.6 <= c['similarity'] < 0.8]

    if high_similarity:
        top = high_similarity[0]
        return (
            f"⚠️ HIGH RISK: New keyword is {int(top['similarity']*100)}% similar to "
            f"'{top['keyword']}' ({top['slug']}). Consider:\n"
            f"   1. Updating the existing article instead\n"
            f"   2. Consolidating content into one comprehensive guide\n"
            f"   3. Differentiating with a distinct angle"
        )
    elif medium_similarity:
        return (
            f"⚡ MODERATE RISK: Found {len(medium_similarity)} similar article(s). "
            f"Ensure your content has a distinct focus to avoid competing with yourself."
        )

    return "✅ Low cannibalization risk. Proceed with caution."


# ============================================================================
# FULL VALIDATION PIPELINE
# ============================================================================

def validate_article(content: str, keyword: str = None,
                     posts_dir: str = "site/content/posts") -> Dict:
    """
    Run full SEO validation on an article.

    Returns:
        Comprehensive validation report
    """
    report = {
        'valid': True,
        'issues': [],
        'warnings': [],
        'fixes_applied': []
    }

    # 1. Validate links
    link_validation = validate_markdown_links(content)
    if not link_validation['valid']:
        report['valid'] = False
    report['link_issues'] = link_validation['issues']

    # 2. Check for cannibalization
    if keyword:
        conflicts = detect_cannibalization(keyword, posts_dir=posts_dir)
        report['cannibalization'] = {
            'conflicts': conflicts,
            'recommendation': get_cannibalization_recommendation(conflicts)
        }
        if any(c['similarity'] >= 0.8 for c in conflicts):
            report['warnings'].append("High keyword cannibalization risk detected")

    # 3. Check alt text quality
    alt_pattern = r'!\[([^\]]*)\]'
    alt_texts = re.findall(alt_pattern, content)
    generic_alts = [alt for alt in alt_texts if
                    alt.endswith('- hero image') or
                    alt.endswith('- section image') or
                    len(alt) < 20]
    if generic_alts:
        report['warnings'].append(f"Found {len(generic_alts)} generic/short alt texts")
        report['generic_alt_texts'] = generic_alts

    return report


def fix_article_issues(content: str) -> Tuple[str, List[str]]:
    """
    Automatically fix common issues in article content.

    Returns:
        Tuple of (fixed_content, list_of_fixes_applied)
    """
    fixes = []

    # Fix nested links
    content, nested_fixes = fix_nested_links(content)
    if nested_fixes > 0:
        fixes.append(f"Fixed {nested_fixes} nested link(s)")

    # Fix duplicate disclosures
    content, disclosure_fixes = fix_duplicate_disclosures(content)
    if disclosure_fixes > 0:
        fixes.append(f"Removed {disclosure_fixes} duplicate disclosure(s)")

    return content, fixes


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python seo_validator.py <article.md> [keyword]")
        print("       python seo_validator.py --check-cannibalization <keyword>")
        sys.exit(1)

    if sys.argv[1] == "--check-cannibalization":
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        if not keyword:
            print("Please provide a keyword to check")
            sys.exit(1)

        print(f"\n🔍 Checking cannibalization for: '{keyword}'")
        print("=" * 60)

        conflicts = detect_cannibalization(keyword)

        if not conflicts:
            print("✅ No conflicts found!")
        else:
            print(f"Found {len(conflicts)} potential conflict(s):\n")
            for c in conflicts:
                print(f"  📄 {c['slug']}")
                print(f"     Keyword: {c['keyword']}")
                print(f"     Similarity: {int(c['similarity']*100)}%")
                print()

        print(get_cannibalization_recommendation(conflicts))

    else:
        article_path = sys.argv[1]
        keyword = sys.argv[2] if len(sys.argv) > 2 else None

        print(f"\n🔍 Validating: {article_path}")
        print("=" * 60)

        with open(article_path, 'r') as f:
            content = f.read()

        # Run validation
        report = validate_article(content, keyword)

        # Show results
        if report['valid']:
            print("✅ Article passed validation!")
        else:
            print("❌ Validation failed!")

        if report.get('link_issues'):
            print(f"\nLink Issues ({len(report['link_issues'])}):")
            for issue in report['link_issues']:
                icon = "🔴" if issue['severity'] == 'critical' else "🟡"
                print(f"  {icon} {issue['description']}")

        if report.get('warnings'):
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  ⚠️  {warning}")

        if report.get('cannibalization', {}).get('conflicts'):
            print(f"\nCannibalization Check:")
            print(f"  {report['cannibalization']['recommendation']}")

        # Offer to fix
        if report.get('link_issues') or report.get('warnings'):
            print("\n" + "-" * 60)
            response = input("Apply automatic fixes? (y/n): ")
            if response.lower() == 'y':
                fixed_content, fixes = fix_article_issues(content)
                if fixes:
                    with open(article_path, 'w') as f:
                        f.write(fixed_content)
                    print(f"✅ Applied fixes:")
                    for fix in fixes:
                        print(f"   • {fix}")
                else:
                    print("No automatic fixes available for these issues.")
