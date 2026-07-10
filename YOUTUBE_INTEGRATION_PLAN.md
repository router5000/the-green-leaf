# YouTube Video Integration - Implementation Plan

## 📋 Overview
Integrate YouTube video search into the cannabiscare content engine to automatically find and embed 1-2 relevant YouTube videos in each article.

**Status:** Planning Complete - Ready for Implementation
**YouTube API Key:** AIzaSyDGZzc5E1ajHyyyKmH205p-7sx0hIC4iE4
**Estimated Implementation Time:** 30-45 minutes
**Additional Cost per Article:** ~$0.01-0.02 (Claude evaluation only, YouTube API is free up to 10,000 units/day)

---

## 🎯 What This Will Do

### Video Placement Strategy
1. **Hero Video** (Position 1): Embedded directly under the H1 title, before hero image
2. **Section Video** (Position 2): Embedded in the lower third of article (replaces/supplements section image)

### Quality Control
- AI evaluation scores each video for relevance (1-10 scale)
- Only videos scoring 7.0+ are included
- Falls back gracefully if no relevant videos found
- Optional: Can restrict to curated cannabis channels only

---

## 📁 Files to Modify/Create

### ✅ Files Already In Place
- ✅ `YT Transfer/youtube_search.py` - Core video search logic
- ✅ `YT Transfer/YOUTUBE_INTEGRATION_GUIDE.md` - Integration guide

### 🔧 Files to Modify
1. **`content_generator.py`** (Line ~758-768)
   - Add youtube_search import
   - Add video search step after affiliate links
   - Add youtube data to frontmatter

2. **`.env`** (Add YouTube API key)
   - Add: `YOUTUBE_API_KEY=AIzaSyDGZzc5E1ajHyyyKmH205p-7sx0hIC4iE4`

3. **`site/src/app/articles/[slug]/page.tsx`** (Line ~183-253)
   - Add YouTubeEmbed component
   - Render hero video before featured image
   - Render section video in content area

4. **`site/src/lib/posts.ts`** (Line ~9-24)
   - Add youtube field to PostData interface
   - Parse youtube array from frontmatter

---

## 📝 Detailed Implementation Steps

### Phase 1: Backend Integration (Python)

#### Step 1.1: Move youtube_search.py to project root
```bash
mv "YT Transfer/youtube_search.py" ./youtube_search.py
```

#### Step 1.2: Add YouTube API key to .env
```env
# Add at end of .env file
YOUTUBE_API_KEY=AIzaSyDGZzc5E1ajHyyyKmH205p-7sx0hIC4iE4
```

#### Step 1.3: Modify content_generator.py

**Location: Line 24-25 (with other imports)**
```python
from youtube_search import find_videos_for_article, format_video_for_frontmatter
```

**Location: Line 765 (after affiliate link insertion, before return statement)**
```python
    # ============================================
    # YOUTUBE VIDEO SEARCH
    # ============================================
    print("\n📺 Searching for relevant YouTube videos...")

    try:
        videos = find_videos_for_article(
            keyword=keyword,
            article_title=article_data["title"],
            article_summary=article_data["meta_description"],
            use_curated_only=False,  # Set True to only use curated channels
            min_score=7.0,
            max_videos=2
        )

        if videos:
            # Format for frontmatter
            youtube_videos = [format_video_for_frontmatter(v) for v in videos]
            article_data["youtube"] = youtube_videos
            print(f"   ✅ Found {len(youtube_videos)} relevant video(s)")

            # Assign positions: first video = hero, second = section
            if len(youtube_videos) >= 1:
                youtube_videos[0]["position"] = "hero"
            if len(youtube_videos) >= 2:
                youtube_videos[1]["position"] = "section"
        else:
            article_data["youtube"] = []
            print("   ⚠️  No relevant videos found")

    except Exception as e:
        print(f"   ❌ Video search error: {e}")
        article_data["youtube"] = []
```

**Location: Line 797 (in save_to_notion_format function, add to frontmatter_dict)**
```python
    # Add after line 792 (estimated_read_time)
    if article.get('youtube'):
        frontmatter_dict['youtube'] = article['youtube']
```

**Location: Line 820 (in format_frontmatter function, add youtube section)**
```python
    # Add after images section, before content
    if 'youtube' in data and data['youtube']:
        frontmatter += "youtube:\n"
        for video in data['youtube']:
            frontmatter += f'  - id: "{video["id"]}"\n'
            frontmatter += f'    title: "{video["title"].replace(chr(34), chr(39))}"\n'  # Replace quotes
            frontmatter += f'    channel: "{video["channel"]}"\n'
            frontmatter += f'    position: "{video.get("position", "hero")}"\n'
```

---

### Phase 2: Frontend Integration (Next.js/TypeScript)

#### Step 2.1: Update PostData interface in posts.ts

**Location: site/src/lib/posts.ts - Line 9-24**

Add youtube field to interface:
```typescript
export interface PostData {
  slug: string
  title: string
  meta_description: string
  keyword: string
  featured_image?: string
  featured_image_alt?: string
  tags: string[]
  status: string
  generated_at: string
  season: string
  estimated_read_time: string
  word_count: number
  content?: string
  contentHtml?: string
  youtube?: Array<{
    id: string
    title: string
    channel: string
    position: 'hero' | 'section'
    thumbnail?: string
    relevance_score?: number
  }>
}
```

#### Step 2.2: Add YouTubeEmbed component to page.tsx

**Location: site/src/app/articles/[slug]/page.tsx - After line 4 (after imports)**

```typescript
// YouTube Video Embed Component
function YouTubeEmbed({
  videoId,
  title,
  channel
}: {
  videoId: string
  title: string
  channel: string
}) {
  return (
    <div className="my-8">
      <div className="aspect-video rounded-xl overflow-hidden shadow-lg">
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?rel=0`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="w-full h-full"
        />
      </div>
      <p className="text-sm text-gray-500 mt-2 text-center">
        📺 {title} • {channel}
      </p>
    </div>
  )
}
```

#### Step 2.3: Render videos in article layout

**Location: site/src/app/articles/[slug]/page.tsx - Line 247 (after article header)**

Replace the section between line 247 and 253 with:

```typescript
        {/* Article Content Section */}
        <div>
          {/* Hero YouTube Video (if present) - before hero image */}
          {post.youtube?.find(v => v.position === 'hero') && (
            <YouTubeEmbed
              videoId={post.youtube.find(v => v.position === 'hero')!.id}
              title={post.youtube.find(v => v.position === 'hero')!.title}
              channel={post.youtube.find(v => v.position === 'hero')!.channel}
            />
          )}

          {/* Article Content - Semantic HTML structure */}
          <div
            className="prose prose-lg max-w-none prose-img:rounded-xl prose-img:shadow-md prose-headings:scroll-mt-20"
            itemProp="articleBody"
            dangerouslySetInnerHTML={{ __html: post.contentHtml || '' }}
          />

          {/* Section YouTube Video (if present) - after content, before tags */}
          {post.youtube?.find(v => v.position === 'section') && (
            <YouTubeEmbed
              videoId={post.youtube.find(v => v.position === 'section')!.id}
              title={post.youtube.find(v => v.position === 'section')!.title}
              channel={post.youtube.find(v => v.position === 'section')!.channel}
            />
          )}
        </div>
```

---

## 🧪 Testing Plan

### Test 1: Standalone Video Search
```bash
cd /Users/jacobtaylor/Desktop/Cannabis\ Care\ Center\ 2025/cannabiscare-content-engine
python3 youtube_search.py "best time to fertilize cannabis"
```

**Expected Output:**
- Should find 15 videos
- Evaluate each with Claude for relevance
- Return top 2 videos with scores 7.0+
- Display video titles, channels, scores, and URLs

### Test 2: Full Article Generation
```bash
python3 content_generator.py --keyword "how to aerate cannabis in fall" --count 1
```

**Expected Output:**
- Article generated with content
- YouTube video search runs
- 1-2 videos found and evaluated
- Frontmatter includes `youtube:` section with video data
- Draft saved to `drafts/` folder

### Test 3: Frontend Rendering
```bash
cd site
npm run dev
```

1. Move test article from drafts to content/posts
2. Visit http://localhost:3000/articles/[slug]
3. Verify:
   - Hero video renders under title
   - Section video renders after content
   - Videos are responsive and embedded properly
   - Fallback works if no videos present

---

## ⚠️ Important Considerations

### API Quota Management
- **YouTube API Quota:** 10,000 units/day (free)
- **Search cost:** ~100 units per article
- **Capacity:** ~100 articles/day before quota exhaustion
- **Reset:** Daily at midnight Pacific Time

### Quality Control
- Minimum relevance score set to 7.0/10
- Can be adjusted higher (8.0) for stricter filtering
- Can enable `use_curated_only=True` to only search trusted channels

### Curated Channels (Optional Enhancement)
The youtube_search.py already includes curated channels:
- The Cannabis Nut
- Ryan Knorr Cannabis
- How To With Doc
- Cannabis Tips
- Silver Cymbal

**To use curated only:** Change `use_curated_only=False` to `use_curated_only=True` in content_generator.py

### Error Handling
- Gracefully falls back if YouTube API fails
- Articles generate successfully even without videos
- No videos = no youtube frontmatter field (frontend handles gracefully)

---

## 📊 Cost Analysis

### Per Article Breakdown
| Item | Cost | Notes |
|------|------|-------|
| YouTube Search API | $0.00 | Free (10k units/day) |
| Video stats enrichment | $0.00 | 1 unit per video |
| Claude evaluation | $0.01-0.02 | Sonnet 4 analyzing 15 videos |
| **Total per article** | **$0.01-0.02** | Very affordable |

### Monthly Projections
- 50 articles/month: ~$0.50-1.00
- 100 articles/month: ~$1.00-2.00
- Negligible impact on overall budget

---

## 🚀 Deployment Steps

After implementation and testing:

1. **Commit changes:**
```bash
git add .
git commit -m "Add YouTube video integration to articles

- Integrate youtube_search.py for AI-evaluated video discovery
- Add YouTube embeds to article template (hero + section positions)
- Update frontmatter schema to include video metadata
- Add graceful fallbacks for articles without videos

🤖 Generated with Claude Code"
```

2. **Push to GitHub:**
```bash
git push origin main
```

3. **Vercel auto-deploys** within 60 seconds

4. **Verify on production:**
   - Visit strainreport.com
   - Check a few articles for video embeds
   - Test responsive behavior on mobile

---

## 🎬 Expected User Experience

### Before YouTube Integration
- Article with hero image banner
- Text content with inline section image
- Related articles at bottom

### After YouTube Integration
- Article title
- **→ YouTube video (most relevant)**
- Hero image banner (still present)
- Text content
- **→ YouTube video (secondary relevant video)** OR section image
- Related articles at bottom

### Benefits
1. **Increased engagement** - Video content keeps visitors on page longer
2. **Better learning** - Visual demonstrations complement written guides
3. **SEO boost** - Rich media signals to search engines
4. **Authority** - Curated professional content from trusted channels
5. **User trust** - Videos from established cannabis experts

---

## ✅ Implementation Checklist

### Python Backend
- [ ] Move youtube_search.py to project root
- [ ] Add YOUTUBE_API_KEY to .env
- [ ] Import youtube_search functions in content_generator.py
- [ ] Add video search step after affiliate links
- [ ] Add youtube data to frontmatter dict
- [ ] Update format_frontmatter to output youtube YAML
- [ ] Test standalone: `python3 youtube_search.py "test query"`
- [ ] Test generation: `python3 content_generator.py --keyword "test" --count 1`

### TypeScript Frontend
- [ ] Add youtube field to PostData interface in posts.ts
- [ ] Add YouTubeEmbed component to page.tsx
- [ ] Render hero video before content
- [ ] Render section video after content
- [ ] Test locally: `npm run dev`
- [ ] Verify responsive design on mobile viewport
- [ ] Check accessibility (iframe titles, etc.)

### Deployment
- [ ] Commit all changes
- [ ] Push to GitHub
- [ ] Verify Vercel deployment succeeds
- [ ] Test on production (strainreport.com)
- [ ] Generate 2-3 new articles with videos
- [ ] Confirm videos display correctly

---

## 🐛 Potential Issues & Solutions

### Issue: "No videos found"
**Solution:**
- Check YOUTUBE_API_KEY is set correctly in .env
- Try broader search terms
- Lower min_score temporarily to 6.0
- Check API quota hasn't been exceeded

### Issue: "Videos not relevant to article"
**Solution:**
- Increase min_score to 8.0 or 8.5
- Enable use_curated_only=True
- Add more trusted channels to CURATED_CHANNELS list

### Issue: "API quota exceeded"
**Solution:**
- Wait until midnight PT (quota resets)
- Reduce MAX_SEARCH_RESULTS from 15 to 10
- Cache video results for similar keywords
- Consider upgrading to paid YouTube API tier (unlikely needed)

### Issue: "Videos not displaying on frontend"
**Solution:**
- Check browser console for errors
- Verify youtube field exists in frontmatter
- Confirm PostData interface includes youtube
- Test iframe embed URL manually
- Check for Content Security Policy blocks

---

## 📚 References

- YouTube Data API v3: https://developers.google.com/youtube/v3
- YouTube Embed Parameters: https://developers.google.com/youtube/player_parameters
- Claude API (Sonnet 4): https://docs.anthropic.com/
- Original Integration Guide: `YT Transfer/YOUTUBE_INTEGRATION_GUIDE.md`

---

## ✨ Future Enhancements (Optional)

1. **Video caching** - Cache search results to reduce API calls
2. **More channels** - Expand CURATED_CHANNELS list with more cannabis YouTubers
3. **Video thumbnails** - Display custom thumbnails instead of immediate embed
4. **User preferences** - Let users toggle video auto-play
5. **Video analytics** - Track which videos get most engagement
6. **Playlist creation** - Auto-generate playlists by topic/season

---

**Status:** ✅ Plan Complete - Ready for Implementation
**Confidence Level:** High (all dependencies in place, clear implementation path)
**Risk Level:** Low (graceful fallbacks, no breaking changes to existing system)
