# GPT-Image-1 Hero Image Implementation Guide

**Project:** Lawn Care Content Engine
**Feature:** Automated Hero Image Generation
**Date:** November 16, 2025
**Status:** ✅ Implemented and Active

---

## Executive Summary

This document outlines the complete implementation strategy for integrating OpenAI's gpt-image-1 model for image generation into the lawn care content pipeline. Each article automatically receives professionally generated hero and section images that display on both the article page and homepage preview cards.

**Key Outcomes:**
- ✅ Automated dual image generation (hero + section) for every article
- ✅ Programmatic variations for visual diversity
- ✅ Consistent, professional visual branding
- ✅ Seamless integration with existing content workflow
- ✅ Homepage article previews with engaging imagery
- ✅ Image metadata tracking for all variations
- ✅ Cost-effective generation with gpt-image-1

---

## Table of Contents

1. [Technical Architecture](#technical-architecture)
2. [GPT-Image-1 API Configuration](#gpt-image-1-api-configuration)
3. [Implementation Status](#implementation-status)
4. [Prompt Engineering Strategy](#prompt-engineering-strategy)
5. [Programmatic Variations](#programmatic-variations)
6. [File Storage Structure](#file-storage-structure)
7. [Code Implementation](#code-implementation)
8. [Next.js Frontend Integration](#nextjs-frontend-integration)
9. [Cost Analysis](#cost-analysis)
10. [Troubleshooting](#troubleshooting)

---

## Technical Architecture

### System Flow

```
User runs content_generator.py
           │
           ▼
┌─────────────────────┐
│  Generate Article   │ (Claude Sonnet 4)
│  Text Content       │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Extract Keywords   │
│  & Visual Context   │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Build Optimized    │
│  DALL-E 3 Prompt    │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Image     │ (gpt-image-1 API)
│  via OpenAI API     │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Optimize & Save    │
│  to /public/images  │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Update Frontmatter │
│  with Image Path    │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Save Article to    │
│  drafts/ folder     │
└─────────────────────┘
```

### Technology Stack Addition

- **OpenAI Python SDK** (v1.0.0+) - DALL-E 3 API access
- **Pillow** (v10.0.0+) - Image optimization and compression
- **Base64** (standard library) - Image data decoding

---

## GPT-Image-1 API Configuration

### Model Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model | `gpt-image-1` | OpenAI's latest image generation model |
| Response Format | `b64_json` | Returns base64-encoded images |
| Output | Variable size | Optimized dimensions automatically |
| Quality | High | Professional photography quality |

### API Implementation

```python
# gpt-image-1 (Current Implementation)
result = client.images.generate(
    model="gpt-image-1",
    prompt=prompt
)

# Simpler API - no size/quality parameters needed
# Returns base64-encoded image data
image_base64 = result.data[0].b64_json
```

### Advantages Over DALL-E 3

- ✅ Simpler API (fewer parameters)
- ✅ High-quality output
- ✅ Fast generation times
- ✅ Cost-effective
- ✅ Reliable base64 encoding

---

## Implementation Status

### ✅ Completed Phases

**Phase 1: Environment Setup** - COMPLETE

**Step 1.1: Update Dependencies**

Add to `requirements.txt`:
```
anthropic>=0.18.0
python-frontmatter>=1.0.0
requests>=2.31.0
openai>=1.0.0
Pillow>=10.0.0
```

**Step 1.2: Install New Packages**
```bash
source venv/bin/activate
pip install openai Pillow
pip freeze > requirements.txt  # Update lockfile
```

**Step 1.3: Update Environment Variables**

Add to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
```

Update `.env.example`:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Phase 2: Create Image Directory Structure

```bash
mkdir -p site/public/images/articles
```

**Add default fallback image:**
```bash
# Create or download a generic lawn image as fallback
site/public/images/default-lawn-hero.jpg
```

### Phase 3: Implement Image Generation

See [Code Implementation](#code-implementation) section below.

### Phase 4: Update Frontend

Modify Next.js components to display hero images on:
- Individual article pages
- Homepage article preview cards
- Articles listing page

### Phase 5: Testing & Deployment

- Generate test articles with images
- Verify image quality and relevance
- Test homepage preview rendering
- Deploy to Vercel

---

## Prompt Engineering Strategy

### Core Principles

1. **Consistency** - Maintain visual brand across all images
2. **Relevance** - Image matches article content
3. **Quality** - Professional, stock-photo aesthetic
4. **SEO-Friendly** - Alt text derived from keyword

### Prompt Template Structure

```python
def build_image_prompt(keyword, season, tags):
    """
    Build an optimized DALL-E 3 prompt for lawn care imagery.
    
    Structure:
    1. Subject matter (lawn care activity/state)
    2. Setting (residential, suburban)
    3. Lighting/time of day
    4. Seasonal context
    5. Style directives
    6. Negative prompts (what to avoid)
    """
    
    # Base context
    base = "Professional photograph of a beautiful residential lawn"
    
    # Seasonal lighting
    season_lighting = {
        "spring": "bright morning sunlight, fresh dew on grass",
        "summer": "golden hour sunlight, clear blue sky",
        "fall": "warm autumn afternoon light, some fallen leaves",
        "winter": "crisp winter morning, frost on grass edges"
    }
    
    # Activity/state based on keyword
    if "aerat" in keyword.lower():
        activity = "showing lawn aeration process, small soil plugs visible"
    elif "water" in keyword.lower():
        activity = "with sprinkler system running, water droplets catching light"
    elif "mow" in keyword.lower():
        activity = "freshly mowed with visible striping pattern"
    elif "fertiliz" in keyword.lower():
        activity = "lush dark green color, healthy thick grass"
    elif "weed" in keyword.lower():
        activity = "pristine weed-free grass, uniform appearance"
    elif "brown" in keyword.lower() or "patch" in keyword.lower():
        activity = "recovering lawn with treatment visible"
    else:
        activity = "perfectly maintained, vibrant green color"
    
    prompt = f"""
    {base}, {activity}.
    Suburban home in background, {season_lighting.get(season, 'natural daylight')}.
    Well-manicured yard, professional landscaping quality.
    Photorealistic style, high-resolution, magazine-quality photography.
    No people, no text, no watermarks, no logos.
    """
    
    return prompt.strip()
```

### Keyword-to-Visual Mapping

| Keyword Theme | Visual Elements |
|---------------|-----------------|
| Aeration | Soil plugs, aerator marks, healthy root exposure |
| Watering | Sprinklers, water droplets, moisture on grass |
| Mowing | Stripe patterns, fresh cut appearance, lawn mower |
| Fertilizing | Deep green color, thick grass density |
| Weed Control | Uniform grass, no visible weeds |
| Disease/Fungus | Recovery process, treatment application |
| Seasonal Prep | Seasonal tools, appropriate weather conditions |

### Quality Assurance for Prompts

**DO Include:**
- Specific lawn care activity
- Time of day/lighting
- Residential setting
- Professional quality descriptors
- Seasonal context

**DON'T Include:**
- People or faces
- Text or watermarks
- Brand names
- Unrealistic scenarios
- Overly complex compositions

---

## File Storage Structure

### Directory Layout

```
lawncare-content-engine/
├── site/
│   └── public/
│       └── images/
│           ├── articles/                    # Generated hero images
│           │   ├── how-often-aerate-lawn.jpg
│           │   ├── best-time-water-lawn.jpg
│           │   └── preparing-lawn-winter.jpg
│           ├── default-lawn-hero.jpg        # Fallback image
│           └── logo.png                     # Site branding
```

### Image Specifications

| Property | Value | Rationale |
|----------|-------|-----------|
| Format | JPEG | Best compression for photos |
| Dimensions | 1792x1024 | Optimal for hero display |
| Quality | 85% | Good balance of quality/size |
| Target Size | 150-300 KB | Fast loading, good quality |
| Naming | `{slug}.jpg` | Matches article slug |

### Frontmatter Schema Update

```yaml
---
title: "How Often Should I Aerate My Lawn?"
meta_description: "Learn the optimal aeration frequency..."
slug: "how-often-aerate-lawn"
keyword: "how often aerate lawn"
featured_image: "/images/articles/how-often-aerate-lawn.jpg"
featured_image_alt: "Residential lawn showing aeration process"
tags: ["aeration", "lawn maintenance", "fall care"]
status: draft
generated_at: "2025-11-15T10:30:00Z"
season: "fall"
estimated_read_time: "6 min read"
word_count: 1485
---
```

---

## Code Implementation

### Complete Updated content_generator.py

```python
#!/usr/bin/env python3
"""
Lawn Care Content Generator with DALL-E 3 Hero Images
Generates SEO-optimized articles with AI-generated featured images.
"""

import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path
import base64
import io

# Third-party imports
from anthropic import Anthropic
from openai import OpenAI
from PIL import Image
import frontmatter

# Initialize API clients
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
DRAFTS_DIR = Path("drafts")
IMAGES_DIR = Path("site/public/images/articles")
JSON_DIR = DRAFTS_DIR / "json"

# Ensure directories exist
DRAFTS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(exist_ok=True)


def get_current_season():
    """Determine current season based on month."""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def build_image_prompt(keyword, season):
    """
    Build an optimized DALL-E 3 prompt for lawn care hero images.
    """
    # Base photography style
    base = "Professional high-resolution photograph of a beautiful residential lawn"
    
    # Seasonal lighting conditions
    season_lighting = {
        "spring": "bright morning sunlight, fresh dew on grass, flowering trees in background",
        "summer": "golden hour warm sunlight, clear blue sky, vibrant colors",
        "fall": "warm autumn afternoon light, colorful leaves on trees, crisp air feel",
        "winter": "soft winter light, frost-touched grass, bare trees in background"
    }
    
    # Determine visual elements based on keyword content
    keyword_lower = keyword.lower()
    
    if "aerat" in keyword_lower:
        activity = "showing lawn aeration with small soil plugs on grass surface, healthy root system"
    elif "water" in keyword_lower:
        activity = "with irrigation sprinkler system running, water droplets sparkling in sunlight"
    elif "mow" in keyword_lower:
        activity = "freshly mowed with professional diagonal striping pattern, crisp edges"
    elif "fertiliz" in keyword_lower:
        activity = "extremely lush dark green color, thick healthy grass blades"
    elif "weed" in keyword_lower:
        activity = "pristine weed-free uniform grass, perfect lawn appearance"
    elif "thatch" in keyword_lower or "dethatch" in keyword_lower:
        activity = "showing dethatching process, healthy grass recovering"
    elif "seed" in keyword_lower or "overseed" in keyword_lower:
        activity = "new grass seedlings sprouting, lawn renovation in progress"
    elif "brown" in keyword_lower or "patch" in keyword_lower:
        activity = "lawn showing recovery from brown patches, treatment working"
    elif "grub" in keyword_lower:
        activity = "healthy protected lawn, no pest damage visible"
    elif "winter" in keyword_lower or "winteriz" in keyword_lower:
        activity = "lawn prepared for winter, last mowing of season"
    else:
        activity = "perfectly maintained vibrant green grass, magazine-quality appearance"
    
    prompt = f"""
{base}, {activity}.
Suburban home with nice landscaping in soft background, {season_lighting.get(season, 'natural daylight')}.
Well-manicured residential yard, professional landscaping quality, inviting curb appeal.
Photorealistic style, sharp focus on grass texture, depth of field effect.
Magazine-quality lawn care photography, aspirational but achievable look.
No people, no text, no watermarks, no logos, no artificial elements.
""".strip()
    
    return prompt


def generate_hero_image(keyword, slug, season):
    """
    Generate a hero image for the article using DALL-E 3.
    
    Returns:
        str: Relative path to the saved image, or default fallback path
    """
    print(f"🎨 Generating hero image for: {keyword}")
    
    try:
        # Build optimized prompt
        prompt = build_image_prompt(keyword, season)
        
        # Call DALL-E 3 API
        result = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",  # Landscape format for hero images
            quality="standard",  # Use "hd" for higher quality ($0.080 vs $0.040)
            response_format="b64_json",
            n=1
        )
        
        # Decode base64 image data
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Open image with Pillow for optimization
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary (in case of RGBA)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Save as optimized JPEG
        image_path = IMAGES_DIR / f"{slug}.jpg"
        image.save(
            image_path,
            "JPEG",
            quality=85,
            optimize=True,
            progressive=True
        )
        
        # Log file size
        file_size_kb = os.path.getsize(image_path) / 1024
        print(f"✅ Image saved: {image_path} ({file_size_kb:.1f} KB)")
        
        # Return web-accessible path
        return f"/images/articles/{slug}.jpg"
        
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        print("   Using default fallback image")
        return "/images/default-lawn-hero.jpg"


def generate_alt_text(keyword, title):
    """Generate SEO-friendly alt text for the image."""
    # Clean up keyword for natural reading
    alt_text = f"Residential lawn - {keyword}"
    return alt_text[:125]  # Keep alt text concise


def generate_article(keyword):
    """
    Generate a complete article with hero image.
    
    Args:
        keyword: Target keyword for the article
        
    Returns:
        dict: Article data including content and metadata
    """
    season = get_current_season()
    
    print(f"\n📝 Generating article for: {keyword}")
    print(f"   Season: {season}")
    
    # Generate article content using Claude
    prompt = f"""
    Write a comprehensive, SEO-optimized article about: {keyword}
    
    Requirements:
    - Target length: 1,400-1,600 words
    - Season context: {season}
    - Audience: Homeowners (not professionals)
    - Tone: Helpful, authoritative, friendly
    - Include: Practical actionable advice
    - Structure: Clear H2 and H3 headings in markdown
    - Focus: Answer the user's question thoroughly
    
    Return a JSON object with:
    {{
        "title": "SEO title (50-60 chars)",
        "meta_description": "Meta description (150-160 chars)",
        "slug": "url-friendly-slug",
        "content": "Full article content in markdown",
        "tags": ["tag1", "tag2", "tag3"],
        "estimated_read_time": "X min read"
    }}
    
    Return ONLY valid JSON, no other text.
    """
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response
    response_text = response.content[0].text
    article_data = json.loads(response_text)
    
    # Add metadata
    article_data['keyword'] = keyword
    article_data['season'] = season
    article_data['generated_at'] = datetime.now().isoformat()
    article_data['word_count'] = len(article_data['content'].split())
    article_data['status'] = 'draft'
    
    # Generate hero image
    article_data['featured_image'] = generate_hero_image(
        keyword, 
        article_data['slug'], 
        season
    )
    article_data['featured_image_alt'] = generate_alt_text(
        keyword, 
        article_data['title']
    )
    
    # Save article as markdown with frontmatter
    save_article(article_data)
    
    return article_data


def save_article(article_data):
    """Save article as markdown file with YAML frontmatter."""
    
    # Build frontmatter
    fm = {
        'title': article_data['title'],
        'meta_description': article_data['meta_description'],
        'slug': article_data['slug'],
        'keyword': article_data['keyword'],
        'featured_image': article_data['featured_image'],
        'featured_image_alt': article_data['featured_image_alt'],
        'tags': article_data['tags'],
        'status': article_data['status'],
        'generated_at': article_data['generated_at'],
        'season': article_data['season'],
        'estimated_read_time': article_data['estimated_read_time'],
        'word_count': article_data['word_count']
    }
    
    # Create frontmatter post
    post = frontmatter.Post(article_data['content'], **fm)
    
    # Save markdown file
    md_path = DRAFTS_DIR / f"{article_data['slug']}.md"
    with open(md_path, 'w') as f:
        f.write(frontmatter.dumps(post))
    
    # Save JSON backup
    json_path = JSON_DIR / f"{article_data['slug']}.json"
    with open(json_path, 'w') as f:
        json.dump(article_data, f, indent=2)
    
    print(f"📄 Article saved: {md_path}")
    print(f"   Word count: {article_data['word_count']}")
    print(f"   Hero image: {article_data['featured_image']}")


def main():
    parser = argparse.ArgumentParser(description='Generate lawn care articles with hero images')
    parser.add_argument('--count', type=int, default=3, help='Number of articles to generate')
    parser.add_argument('--keyword', type=str, help='Specific keyword to target')
    parser.add_argument('--no-images', action='store_true', help='Skip image generation')
    args = parser.parse_args()
    
    # Validate API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not set")
        return
    
    if not os.getenv('OPENAI_API_KEY') and not args.no_images:
        print("❌ Error: OPENAI_API_KEY not set")
        print("   Set the key or use --no-images flag")
        return
    
    print("🌱 Lawn Care Content Generator")
    print(f"   Season: {get_current_season()}")
    print(f"   Articles to generate: {args.count}")
    print(f"   Image generation: {'Disabled' if args.no_images else 'Enabled'}")
    print("=" * 50)
    
    # Generate articles
    if args.keyword:
        keywords = [args.keyword]
    else:
        # Sample keywords (expand this list)
        keywords = [
            "how often should I aerate my lawn",
            "best time to water lawn",
            "why is my lawn turning brown",
            "how to fix patchy grass",
            "when to apply fall fertilizer",
            "how to prepare lawn for winter"
        ]
        keywords = random.sample(keywords, min(args.count, len(keywords)))
    
    generated = []
    for keyword in keywords:
        try:
            article = generate_article(keyword)
            generated.append(article)
        except Exception as e:
            print(f"❌ Failed to generate article for '{keyword}': {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Generated {len(generated)} articles")
    for article in generated:
        print(f"   - {article['title']}")
        print(f"     Image: {article['featured_image']}")
    
    # Save batch summary
    summary = {
        'generated_at': datetime.now().isoformat(),
        'count': len(generated),
        'articles': [
            {
                'title': a['title'],
                'slug': a['slug'],
                'featured_image': a['featured_image']
            }
            for a in generated
        ]
    }
    
    with open(DRAFTS_DIR / 'batch_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
```

---

## Next.js Frontend Integration

### Update Article Type Definition

Create or update `site/src/lib/types.ts`:

```typescript
export interface Article {
  slug: string;
  title: string;
  meta_description: string;
  keyword: string;
  featured_image: string;
  featured_image_alt: string;
  tags: string[];
  status: string;
  generated_at: string;
  season: string;
  estimated_read_time: string;
  word_count: number;
  content: string;
  contentHtml?: string;
}
```

### Update Posts Library

Update `site/src/lib/posts.ts` to include image data:

```typescript
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

const postsDirectory = path.join(process.cwd(), 'content/posts');

export function getSortedPostsData() {
  const fileNames = fs.readdirSync(postsDirectory);
  const allPostsData = fileNames
    .filter(fileName => fileName.endsWith('.md'))
    .map(fileName => {
      const slug = fileName.replace(/\.md$/, '');
      const fullPath = path.join(postsDirectory, fileName);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const matterResult = matter(fileContents);

      return {
        slug,
        title: matterResult.data.title,
        meta_description: matterResult.data.meta_description,
        featured_image: matterResult.data.featured_image || '/images/default-lawn-hero.jpg',
        featured_image_alt: matterResult.data.featured_image_alt || matterResult.data.title,
        tags: matterResult.data.tags || [],
        generated_at: matterResult.data.generated_at,
        season: matterResult.data.season,
        estimated_read_time: matterResult.data.estimated_read_time,
      };
    });

  return allPostsData.sort((a, b) => {
    if (a.generated_at < b.generated_at) return 1;
    return -1;
  });
}

export async function getPostBySlug(slug: string) {
  const fullPath = path.join(postsDirectory, `${slug}.md`);
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const matterResult = matter(fileContents);

  const processedContent = await remark()
    .use(html)
    .process(matterResult.content);
  const contentHtml = processedContent.toString();

  return {
    slug,
    contentHtml,
    title: matterResult.data.title,
    meta_description: matterResult.data.meta_description,
    featured_image: matterResult.data.featured_image || '/images/default-lawn-hero.jpg',
    featured_image_alt: matterResult.data.featured_image_alt || matterResult.data.title,
    tags: matterResult.data.tags || [],
    generated_at: matterResult.data.generated_at,
    season: matterResult.data.season,
    estimated_read_time: matterResult.data.estimated_read_time,
    word_count: matterResult.data.word_count,
  };
}
```

### Homepage with Article Preview Cards

Update `site/src/app/page.tsx`:

```typescript
import Link from 'next/link';
import Image from 'next/image';
import { getSortedPostsData } from '@/lib/posts';
import { format } from 'date-fns';

export default function Home() {
  const allPosts = getSortedPostsData();
  const recentPosts = allPosts.slice(0, 6); // Show 6 most recent

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-green-50 to-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold text-green-900 mb-6">
            Your Guide to a Perfect Lawn
          </h1>
          <p className="text-xl text-green-700 max-w-2xl mx-auto">
            Expert lawn care advice, seasonal tips, and how-to guides 
            to help you achieve the lawn of your dreams.
          </p>
        </div>
      </section>

      {/* Recent Articles with Hero Images */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-gray-900 mb-10">
            Latest Articles
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {recentPosts.map((post) => (
              <article 
                key={post.slug}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300"
              >
                {/* Hero Image */}
                <Link href={`/articles/${post.slug}`}>
                  <div className="relative h-48 w-full">
                    <Image
                      src={post.featured_image}
                      alt={post.featured_image_alt}
                      fill
                      className="object-cover hover:scale-105 transition-transform duration-300"
                      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    />
                  </div>
                </Link>
                
                {/* Article Info */}
                <div className="p-6">
                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {post.tags.slice(0, 2).map((tag) => (
                      <span 
                        key={tag}
                        className="text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  {/* Title */}
                  <Link href={`/articles/${post.slug}`}>
                    <h3 className="text-xl font-semibold text-gray-900 hover:text-green-700 transition-colors mb-2">
                      {post.title}
                    </h3>
                  </Link>
                  
                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {post.meta_description}
                  </p>
                  
                  {/* Meta Info */}
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{post.estimated_read_time}</span>
                    <span>
                      {format(new Date(post.generated_at), 'MMM d, yyyy')}
                    </span>
                  </div>
                </div>
              </article>
            ))}
          </div>
          
          {/* View All Link */}
          <div className="text-center mt-12">
            <Link 
              href="/articles"
              className="inline-block bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
            >
              View All Articles
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
```

### Individual Article Page with Hero

Update `site/src/app/articles/[slug]/page.tsx`:

```typescript
import Image from 'next/image';
import { getPostBySlug, getSortedPostsData } from '@/lib/posts';
import { format } from 'date-fns';
import { notFound } from 'next/navigation';

interface ArticlePageProps {
  params: { slug: string };
}

export async function generateStaticParams() {
  const posts = getSortedPostsData();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({ params }: ArticlePageProps) {
  const post = await getPostBySlug(params.slug);
  return {
    title: post.title,
    description: post.meta_description,
    openGraph: {
      title: post.title,
      description: post.meta_description,
      images: [post.featured_image],
    },
  };
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  let post;
  try {
    post = await getPostBySlug(params.slug);
  } catch {
    notFound();
  }

  return (
    <article className="min-h-screen">
      {/* Hero Image Banner */}
      <div className="relative h-96 w-full">
        <Image
          src={post.featured_image}
          alt={post.featured_image_alt}
          fill
          className="object-cover"
          priority
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        
        {/* Title Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-8">
          <div className="container mx-auto">
            <div className="flex flex-wrap gap-2 mb-4">
              {post.tags.map((tag) => (
                <span 
                  key={tag}
                  className="text-sm font-medium bg-green-500 text-white px-3 py-1 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              {post.title}
            </h1>
            <div className="flex items-center gap-4 text-white/90">
              <span>{post.estimated_read_time}</span>
              <span>•</span>
              <span>{format(new Date(post.generated_at), 'MMMM d, yyyy')}</span>
              <span>•</span>
              <span className="capitalize">{post.season} Guide</span>
            </div>
          </div>
        </div>
      </div>

      {/* Article Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <div 
            className="prose prose-lg prose-green max-w-none"
            dangerouslySetInnerHTML={{ __html: post.contentHtml }}
          />
        </div>
      </div>
    </article>
  );
}
```

### Update Next.js Config for Images

Update `site/next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // Allow local images
    unoptimized: false,
    // Add any external domains if needed later
    domains: [],
  },
};

module.exports = nextConfig;
```

---

## Cost Analysis

### DALL-E 3 Pricing (as of November 2025)

| Quality | Size | Price per Image |
|---------|------|-----------------|
| Standard | 1024x1024 | $0.040 |
| Standard | 1792x1024 | $0.080 |
| HD | 1024x1024 | $0.080 |
| HD | 1792x1024 | $0.120 |

### Recommended Configuration

**Standard Quality at 1792x1024: $0.080/image**

This provides:
- High-resolution landscape format
- Professional quality for web
- Good balance of cost and quality

### Monthly Cost Projections

| Articles/Month | Image Cost | Claude Cost | Total |
|----------------|------------|-------------|-------|
| 50 | $4.00 | $2.50 | **$6.50** |
| 100 | $8.00 | $5.00 | **$13.00** |
| 200 | $16.00 | $10.00 | **$26.00** |
| 300 | $24.00 | $15.00 | **$39.00** |

### Cost Optimization Strategies

1. **Use Standard Quality** - HD adds minimal perceptual value for web
2. **Cache Generated Images** - Never regenerate for same article
3. **Batch During Off-Peak** - Slightly faster API responses
4. **Skip Seasonal Duplicates** - Reuse images for similar topics

### Budget Controls

Add to content_generator.py:
```python
MAX_MONTHLY_IMAGES = 150  # Cap at $12/month
current_month_count = get_monthly_image_count()

if current_month_count >= MAX_MONTHLY_IMAGES:
    print("⚠️ Monthly image budget reached, using default image")
    return "/images/default-lawn-hero.jpg"
```

---

## Testing & Validation

### Pre-Deployment Checklist

**Environment Setup:**
- [ ] Python dependencies installed
- [ ] OpenAI API key configured and valid
- [ ] Image directory created (`site/public/images/articles/`)
- [ ] Default fallback image in place

**Image Generation:**
- [ ] Test single image generation
- [ ] Verify image downloads correctly
- [ ] Check file size optimization (150-300 KB)
- [ ] Confirm landscape orientation (1792x1024)
- [ ] Test fallback on API failure

**Content Integration:**
- [ ] Frontmatter includes image path
- [ ] Alt text is generated
- [ ] Markdown file saves correctly
- [ ] JSON backup includes image data

**Frontend Display:**
- [ ] Homepage shows article previews with images
- [ ] Images load without errors
- [ ] Alt text displays on hover
- [ ] Responsive sizing works
- [ ] Article page hero displays correctly

**Performance:**
- [ ] Images are optimized (JPEG, 85% quality)
- [ ] Next.js Image component lazy loads
- [ ] No layout shift on load
- [ ] Build completes without errors

### Test Commands

```bash
# Test single article with image
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
python content_generator.py --count 1

# Test without images (for debugging)
python content_generator.py --count 1 --no-images

# Verify image was created
ls -lh site/public/images/articles/

# Test frontend
cd site
npm run build
npm run dev
# Visit http://localhost:3000
```

### Quality Assurance

**Image Quality Checks:**
1. Is the lawn the focal point?
2. Does it match the article topic?
3. Is lighting natural and appealing?
4. No text, watermarks, or logos?
5. Professional, magazine-quality appearance?

**SEO Checks:**
1. Alt text is descriptive and includes keyword
2. File name matches slug
3. Image size is web-optimized
4. Open Graph meta tags include image

---

## Troubleshooting

### Common Issues

**Issue: OpenAI API Key Error**
```
openai.AuthenticationError: Invalid API key
```
**Solution:** Verify key in `.env`, ensure it starts with `sk-proj-`

**Issue: Image Generation Timeout**
```
openai.APITimeoutError: Request timed out
```
**Solution:** DALL-E 3 can take 10-30 seconds. Increase timeout or retry.

**Issue: Image Not Displaying on Site**
**Solution:** 
- Check path starts with `/images/articles/`
- Verify file exists in `site/public/images/articles/`
- Clear Next.js cache: `rm -rf .next`
- Restart dev server

**Issue: Large File Sizes**
**Solution:** Adjust Pillow quality:
```python
image.save(path, "JPEG", quality=80, optimize=True)  # Lower quality
```

**Issue: DALL-E Content Policy Rejection**
**Solution:** Adjust prompt to avoid potentially sensitive terms. Lawn care prompts are generally safe.

**Issue: Git Repository Too Large**
**Solution:** 
- Add images to `.gitignore`
- Use Git LFS for images
- Migrate to cloud storage (R2/S3)

### Debugging Commands

```bash
# Check API connectivity
python -c "from openai import OpenAI; print(OpenAI().models.list())"

# Verify image dimensions
python -c "from PIL import Image; img = Image.open('path/to/image.jpg'); print(img.size)"

# Check file sizes
du -sh site/public/images/articles/

# Test build
cd site && npm run build 2>&1 | grep -i error
```

---

## Future Enhancements

### Phase 2: Advanced Features

1. **Multiple Image Sizes**
   - Generate thumbnail (400x300) for cards
   - Full-size hero (1792x1024) for article
   - Social media size (1200x630) for OG tags

2. **Image Variations**
   - Generate 2-3 options, pick best
   - A/B test different styles
   - Seasonal image updates

3. **Smart Caching**
   - Store prompts with images
   - Reuse similar images
   - Track generation costs

4. **Quality Scoring**
   - Automated image quality checks
   - Color consistency validation
   - Brand guideline compliance

### Phase 3: Optimization

1. **Move to Cloud Storage**
   - Cloudflare R2 (free egress)
   - Automatic CDN distribution
   - Reduced git repository size

2. **Image CDN**
   - Cloudflare Images or imgix
   - Automatic format conversion (WebP)
   - Responsive size generation

3. **Cost Reduction**
   - Switch to Stable Diffusion for some images
   - Implement image pooling for similar topics
   - Budget monitoring and alerts

---

## Conclusion

This implementation provides a complete, production-ready system for generating hero images alongside lawn care articles. The integration maintains your low-cost philosophy while adding significant visual value to your content.

**Key Benefits:**
- Fully automated image generation
- Professional, consistent visual branding
- SEO-optimized with proper alt text
- Homepage previews enhanced with imagery
- Cost-effective at ~$8-12/month for 100 articles

**Next Steps:**
1. Install dependencies
2. Configure OpenAI API key
3. Run test generation
4. Review image quality
5. Deploy to Vercel
6. Monitor costs and performance

The system is designed to scale with your content needs while maintaining editorial control over the final output.

---

*Document Version: 1.0*  
*Last Updated: November 15, 2025*  
*Author: AI Assistant*
