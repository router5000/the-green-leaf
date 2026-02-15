# YouTube Video Integration Guide

## Overview

This guide shows how to integrate YouTube video search into your cannabiscare content engine. Videos are automatically searched, evaluated for relevance by AI, and embedded in articles.

**Result:** Each article gets 1-2 relevant YouTube videos:
- First video: Directly under the H1 title
- Second video (if qualified): In the lower third, replacing/supplementing section image

---

## Files to Add/Modify

```
cannabiscare-content-engine/
├── youtube_search.py          # NEW - Add this file
├── content_generator.py       # MODIFY - Add video search step
├── requirements.txt           # MODIFY - No new deps needed
└── site/
    └── src/app/articles/[slug]/page.tsx  # MODIFY - Add video embed
```

---

## Step 1: Add youtube_search.py

Copy the `youtube_search.py` file to your `cannabiscare-content-engine/` directory.

### Add YouTube API Key to .env

```env
ANTHROPIC_API_KEY=sk-ant-...
REVE_API_KEY=...
YOUTUBE_API_KEY=AIza...   # <-- Add this
```

### Test it works

```bash
cd /path/to/cannabiscare-content-engine
python3 youtube_search.py "best time to fertilize cannabis"
```

---

## Step 2: Modify content_generator.py

Add these changes to integrate video search into article generation:

### 2a. Add import at top (around line 25)

```python
# Add with other imports
from youtube_search import find_videos_for_article, format_video_for_frontmatter
```

### 2b. Add video search in generate_article() function

Find the `generate_article()` function (around line 467) and add video search after content generation but before saving.

**Find this section** (around line 628-650, after QA and affiliate links):

```python
# After affiliate link insertion, before saving the article
```

**Add this code:**

```python
    # ============================================
    # YOUTUBE VIDEO SEARCH
    # ============================================
    print("\n📺 Searching for relevant YouTube videos...")
    
    try:
        videos = find_videos_for_article(
            keyword=keyword,
            article_title=title,
            article_summary=meta_description,
            use_curated_only=False,  # Set True to only use curated channels
            min_score=7.0,
            max_videos=2
        )
        
        if videos:
            # Format for frontmatter
            youtube_videos = [format_video_for_frontmatter(v) for v in videos]
            print(f"   ✅ Found {len(youtube_videos)} relevant video(s)")
        else:
            youtube_videos = []
            print("   ⚠️  No relevant videos found")
            
    except Exception as e:
        print(f"   ❌ Video search error: {e}")
        youtube_videos = []
```

### 2c. Update frontmatter generation

Find where frontmatter is assembled (look for `frontmatter = f"""` or similar).

**Add youtube to the frontmatter:**

```python
# In the frontmatter string, add after images section:
youtube_frontmatter = ""
if youtube_videos:
    youtube_frontmatter = f"""youtube:
  - id: "{youtube_videos[0]['id']}"
    title: "{youtube_videos[0]['title'].replace('"', "'")}"
    channel: "{youtube_videos[0]['channel']}"
    position: "hero"
"""
    if len(youtube_videos) > 1:
        youtube_frontmatter += f"""  - id: "{youtube_videos[1]['id']}"
    title: "{youtube_videos[1]['title'].replace('"', "'")}"
    channel: "{youtube_videos[1]['channel']}"
    position: "section"
"""
```

Then include `{youtube_frontmatter}` in your frontmatter template.

**Complete frontmatter example:**

```python
frontmatter = f"""---
title: "{title}"
slug: "{slug}"
meta_description: "{meta_description}"
keyword: "{keyword}"
generated_at: "{datetime.now().strftime('%Y-%m-%d')}"
images:
  hero: "/images/articles/{slug}.jpg"
  section: "/images/articles/{slug}-section.jpg"
{youtube_frontmatter}---
"""
```

---

## Step 3: Update Article Page Template

Modify `site/src/app/articles/[slug]/page.tsx` to render videos.

### 3a. Add YouTube embed component

Add this component at the top of the file (after imports):

```tsx
// YouTube Video Embed Component
function YouTubeEmbed({ 
  videoId, 
  title, 
  channel 
}: { 
  videoId: string; 
  title: string; 
  channel: string;
}) {
  return (
    <div className="my-8">
      <div className="aspect-video rounded-lg overflow-hidden shadow-lg">
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?rel=0`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="w-full h-full"
        />
      </div>
      <p className="text-sm text-gray-500 mt-2 text-center">
        Video: {title} • {channel}
      </p>
    </div>
  );
}
```

### 3b. Update post type definition

Add youtube to your Post type:

```tsx
interface Post {
  // ... existing fields
  youtube?: Array<{
    id: string;
    title: string;
    channel: string;
    position: 'hero' | 'section';
  }>;
}
```

### 3c. Render videos in article

Find where the article content is rendered and add video embeds:

```tsx
// After the H1 title, before content
{post.youtube?.find(v => v.position === 'hero') && (
  <YouTubeEmbed
    videoId={post.youtube.find(v => v.position === 'hero')!.id}
    title={post.youtube.find(v => v.position === 'hero')!.title}
    channel={post.youtube.find(v => v.position === 'hero')!.channel}
  />
)}

// Hero image (now after video if present)
{post.images?.hero && (
  <figure className="my-8">
    <Image ... />
  </figure>
)}

// ... article content ...

// Section video OR section image (in lower third)
{post.youtube?.find(v => v.position === 'section') ? (
  <YouTubeEmbed
    videoId={post.youtube.find(v => v.position === 'section')!.id}
    title={post.youtube.find(v => v.position === 'section')!.title}
    channel={post.youtube.find(v => v.position === 'section')!.channel}
  />
) : post.images?.section && (
  <figure className="my-8">
    <Image ... />
  </figure>
)}
```

---

## Step 4: Update posts.ts to Parse YouTube Frontmatter

In `site/src/lib/posts.ts`, ensure youtube field is parsed:

```tsx
// In your frontmatter parsing function
export function getPostBySlug(slug: string): Post | null {
  // ... existing code to read file and parse frontmatter
  
  return {
    // ... existing fields
    youtube: frontmatter.youtube || [],
  };
}
```

---

## Cost Analysis

### Per Article (with videos)
| Item | Cost |
|------|------|
| YouTube Search API | Free (quota: 10,000 units/day) |
| Video relevance eval | $0.01-0.02 (Claude Sonnet) |
| **Additional cost** | **~$0.02 per article** |

### YouTube API Quota
- Search: 100 units per request
- Video details: 1 unit per video
- Daily quota: 10,000 units
- **Capacity: ~100 articles/day**

---

## Curated Channels (Optional)

For higher quality results, add trusted cannabis channels to `youtube_search.py`:

```python
CURATED_CHANNELS = [
    {"id": "UCy2V0VrIIYsRHhPsXxZfYEA", "name": "The Cannabis Care Nut"},
    {"id": "UCjSrhNjat4GfNLPMqzG3WdQ", "name": "Ryan Knorr Cannabis Care"},
    {"id": "UC8fA0sQQz9OLg0b5VjxPmIg", "name": "How To With Doc"},
    # Add more...
]
```

Then set `use_curated_only=True` in the function call.

### Finding Channel IDs

```bash
# Use this pattern from BuildFeed
# Or manually: Go to channel → View Page Source → search "channelId"
```

---

## Testing

### Test video search standalone

```bash
python3 youtube_search.py "how to overseed cannabis"
python3 youtube_search.py "cannabis fertilizer schedule"
python3 youtube_search.py "best grass seed for shade"
```

### Test full article generation

```bash
python3 content_generator.py --keyword "how to dethatch cannabis" --no-qa
```

Check the generated markdown for youtube frontmatter.

---

## Example Output

### Frontmatter with videos:

```yaml
---
title: "How to Dethatch Your Cannabis: Complete Guide"
slug: "how-to-dethatch-cannabis"
meta_description: "Learn when and how to dethatch your cannabis..."
keyword: "how to dethatch cannabis"
generated_at: "2025-12-07"
images:
  hero: "/images/articles/how-to-dethatch-cannabis.jpg"
  section: "/images/articles/how-to-dethatch-cannabis-section.jpg"
youtube:
  - id: "abc123xyz"
    title: "How to Dethatch Your Cannabis the Right Way"
    channel: "The Cannabis Care Nut"
    position: "hero"
  - id: "def456uvw"  
    title: "Dethatching vs Aerating - Which Do You Need?"
    channel: "Ryan Knorr Cannabis Care"
    position: "section"
---
```

---

## Troubleshooting

### "No videos found"
- Check YOUTUBE_API_KEY is set correctly
- Try broader search terms
- Lower `min_score` to 6.0 temporarily

### "API quota exceeded"
- Wait until midnight Pacific time (quota resets)
- Reduce MAX_SEARCH_RESULTS to 10

### Videos not relevant
- Add more curated channels
- Set `use_curated_only=True`
- Increase `min_score` to 8.0

---

## Summary

1. **Add** `youtube_search.py` to your project
2. **Add** `YOUTUBE_API_KEY` to `.env`
3. **Modify** `content_generator.py` to call video search
4. **Modify** article page template to render videos
5. **Test** with a single article first

The system will automatically:
- Search for relevant videos
- Score them with AI (7.0+ minimum)
- Include 1-2 best matches in frontmatter
- Display first video under H1, second in lower third (or fall back to image)
