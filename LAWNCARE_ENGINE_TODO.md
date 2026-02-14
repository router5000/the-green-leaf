# Lawn Care Content Engine - Master TODO List

**Project:** lawncare.center Automated Content System  
**Purpose:** Task list for Claude Code to execute  
**Created:** November 15, 2025  
**Goal:** Fully automated, monetizable lawn care content site

---

## 🎯 Current State Summary

**✅ COMPLETED (November 15, 2025)**
- ✅ Python content generator with Claude Sonnet 4
- ✅ DALL-E 3 hero image generation integrated (1792x1024 landscape)
- ✅ Smart prompt engineering with seasonal variations
- ✅ Image optimization (JPEG, 85% quality, ~500KB)
- ✅ Next.js site with Tailwind CSS
- ✅ Hero images on homepage and article pages
- ✅ Responsive Image components with hover effects
- ✅ SEO alt text generation
- ✅ Markdown-based content workflow
- ✅ Environment variable support (.env)
- ✅ Comprehensive documentation updated
- ✅ Dev server running successfully (localhost:3001)

**⏳ IN PROGRESS**
- ⏳ Not yet deployed to Vercel
- ⏳ No search functionality
- ⏳ No monetization strategy implemented
- ⏳ Only 1 test article generated so far

---

## 📋 PRIORITY 1: Core Content Improvements

### 1.1 Enhanced Photorealistic Image Generation
**Status:** ✅ PARTIALLY COMPLETE (Basic implementation done)
**Impact:** Higher engagement, professional appearance

```python
# ✅ DONE: Basic DALL-E 3 integration with smart prompts
# ⏳ TODO: Enhanced photorealism tweaks (optional improvement)

Completed:
- [x] Integrated DALL-E 3 API
- [x] Built build_image_prompt() with keyword detection
- [x] Added seasonal lighting variations
- [x] Professional photography language in prompts
- [x] Tested 1 sample image (successful - 565KB)

Optional Enhancements (can do now or later):
- [ ] Add camera/lens specifications (e.g., "Canon EOS R5, 24-70mm")
- [ ] Include depth of field terms: "shallow DOF", "natural bokeh"
- [ ] Test 10 sample images and rate photorealism
- [ ] Iterate on prompt until consistently scoring 8+
```

**Example Enhanced Prompt Structure:**
```
Professional photograph captured with high-end DSLR camera, {subject}.
Shot during {time_of_day}, {lighting_conditions}.
Shallow depth of field with natural bokeh, rule of thirds composition.
Photorealistic, ultra-high resolution, magazine editorial quality.
Color grading: natural, slightly warm tones, high dynamic range.
No artificial elements, no CGI, no illustrations, no text overlays.
```

### 1.2 Mid-Article Section Image Generation
**Status:** TODO  
**Impact:** Improved engagement, lower bounce rate, better SEO

```python
# Add second contextual image in article middle

Tasks:
- [ ] Modify article generation to identify key H2 section for image placement
- [ ] Create function: generate_section_image(section_title, section_content, keyword)
- [ ] Insert image markdown at midpoint of article
- [ ] Generate unique prompt based on specific section content
- [ ] Add section_image and section_image_alt to frontmatter
- [ ] Update Next.js renderer to display mid-article image
- [ ] Ensure image is responsive and properly sized (1024x1024 square for inline)
```

**Implementation Approach:**
```python
def generate_article_with_images(keyword):
    # 1. Generate full article text
    # 2. Parse H2 sections
    # 3. Select middle section (or most visual section)
    # 4. Generate hero image (landscape 1792x1024)
    # 5. Generate section image (square 1024x1024)
    # 6. Insert section image markdown after selected H2
    # 7. Update frontmatter with both image paths
```

### 1.3 Comprehensive Image SEO Optimization
**Status:** TODO  
**Impact:** Image search traffic, accessibility compliance, Core Web Vitals

```markdown
Tasks:
- [ ] Generate descriptive, keyword-rich alt text (125 chars max)
- [ ] Create image title attributes
- [ ] Add structured data (Schema.org ImageObject)
- [ ] Generate image captions for display
- [ ] Create image sitemap (sitemap-images.xml)
- [ ] Implement lazy loading with blur placeholder
- [ ] Add WebP format conversion
- [ ] Optimize file naming: {keyword-slug}-{descriptor}.jpg
```

**Frontmatter Schema Update:**
```yaml
images:
  hero:
    src: "/images/articles/how-aerate-lawn-hero.jpg"
    alt: "Professional lawn aeration showing soil plugs on healthy residential grass"
    title: "Lawn Aeration Process - Soil Plugs on Green Grass"
    caption: "Proper aeration creates small soil plugs that improve drainage and root growth"
    width: 1792
    height: 1024
  section:
    src: "/images/articles/how-aerate-lawn-tools.jpg"
    alt: "Core aerator machine on lawn with visible tines penetrating soil"
    title: "Core Aerator Equipment for Residential Lawns"
    caption: "A core aerator removes small plugs of soil to reduce compaction"
    width: 1024
    height: 1024
```

### 1.4 Shorter, High-Impact Articles
**Status:** TODO  
**Impact:** Better readability, higher completion rates, faster generation

```markdown
Tasks:
- [ ] Reduce target word count from 1400-1600 to 800-1000 words
- [ ] Update Claude prompt to emphasize conciseness
- [ ] Focus on actionable steps over background explanation
- [ ] Use bullet points for key takeaways
- [ ] Add "Quick Answer" summary box at top
- [ ] Implement "TL;DR" section
- [ ] Test readability scores (target: Flesch-Kincaid Grade 8)
```

**Updated Article Structure:**
```markdown
# Title (H1)

**Quick Answer:** [2-3 sentence direct answer to the question]

**Key Takeaways:**
- Point 1
- Point 2
- Point 3

## Understanding [Topic] (H2)
[200-250 words]

[SECTION IMAGE HERE]

## Step-by-Step Guide (H2)
[300-400 words with numbered steps]

## Common Mistakes to Avoid (H2)
[150-200 words]

## When to Call a Professional (H2)
[100-150 words]

---
**Total: 800-1000 words**
```

---

## 📋 PRIORITY 2: Voice & Tone Customization

### 2.1 Brand Voice Configuration System
**Status:** TODO  
**Impact:** Consistent brand identity, reader trust, differentiation

```markdown
Tasks:
- [ ] Create voice_config.json file for brand personality
- [ ] Collect 3-5 writing samples from user (WAITING FOR INPUT)
- [ ] Analyze samples for: tone, vocabulary, sentence structure, personality
- [ ] Create system prompt template that enforces voice
- [ ] Add voice parameters to content_generator.py
- [ ] Test generation with voice samples
- [ ] Create voice consistency scoring mechanism
```

**Voice Configuration File Structure:**
```json
{
  "brand_voice": {
    "personality": "friendly expert neighbor",
    "tone": "conversational but authoritative",
    "formality_level": 3,  // 1=casual, 5=formal
    "humor_level": 2,      // 1=serious, 5=comedic
    "technical_depth": 3,  // 1=beginner, 5=expert
    "empathy_level": 4,    // 1=distant, 5=warm
    
    "vocabulary_preferences": {
      "use": ["you'll want to", "here's the thing", "pro tip"],
      "avoid": ["utilize", "leverage", "synergy", "optimal"]
    },
    
    "sentence_patterns": {
      "avg_length": "medium (15-20 words)",
      "variety": "mix short punchy with longer explanatory",
      "rhetorical_questions": true,
      "contractions": true
    },
    
    "opening_style": "direct answer or relatable scenario",
    "closing_style": "encouraging call-to-action",
    
    "sample_phrases": [
      "Here's the deal:",
      "Trust me on this one",
      "Your lawn will thank you",
      "Let's break this down"
    ]
  }
}
```

**System Prompt Template:**
```python
VOICE_SYSTEM_PROMPT = """
You are writing for lawncare.center with this specific voice:

PERSONALITY: {personality}
TONE: {tone}
APPROACH: Write like a {personality} who genuinely wants to help.

WRITING RULES:
- Use contractions (you're, it's, don't)
- Address reader as "you" directly
- Include phrases like: {sample_phrases}
- Avoid jargon: {avoid_words}
- Ask rhetorical questions to engage
- Keep sentences {avg_length}
- Be encouraging, not preachy

SAMPLE OF DESIRED VOICE:
{writing_samples}

Match this voice exactly while providing accurate lawn care information.
"""
```

### 2.2 User Writing Sample Integration
**Status:** WAITING FOR USER INPUT  

**What I Need From You:**
1. **3-5 paragraphs** of writing in your desired voice
2. Can be from existing content, emails, or written specifically
3. Should demonstrate:
   - How you open/greet
   - How you explain technical concepts
   - Your natural sentence rhythm
   - Words/phrases you naturally use
   - How you encourage/motivate

**Example Request:**
> "Write a paragraph explaining why spring is important for lawn care, in the voice you want for your site."

---

## 📋 PRIORITY 3: Site-Wide NLP Search

### 3.1 Search Infrastructure Selection
**Status:** TODO  
**Impact:** User experience, time on site, SEO (site links)

**Option A: Algolia (Recommended for MVP)**
```markdown
Tasks:
- [ ] Sign up for Algolia free tier (10K searches/month)
- [ ] Install algoliasearch package
- [ ] Create search index schema
- [ ] Build indexing script for articles
- [ ] Implement InstantSearch React component
- [ ] Add search to site header
- [ ] Configure ranking and relevance
```

**Option B: Elasticsearch (Self-hosted, more complex)**
```markdown
- Higher control, steeper learning curve
- Requires server management
- Better for 10K+ articles
```

**Option C: Typesense (Open source alternative)**
```markdown
- Self-hosted or cloud
- Typo tolerance built-in
- Good documentation
```

**Option D: Fuse.js (Client-side, simplest)**
```markdown
- No server needed
- Works for <500 articles
- Bundle size concerns
```

### 3.2 Search Implementation (Algolia Path)
**Status:** TODO

```bash
# Install dependencies
npm install algoliasearch react-instantsearch-dom
```

```typescript
// site/src/lib/algolia.ts
import algoliasearch from 'algoliasearch';

const client = algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!,
  process.env.ALGOLIA_ADMIN_KEY!
);

const index = client.initIndex('articles');

export async function indexArticle(article: Article) {
  await index.saveObject({
    objectID: article.slug,
    title: article.title,
    content: article.content,
    meta_description: article.meta_description,
    tags: article.tags,
    keyword: article.keyword,
    season: article.season,
    // NLP-friendly fields
    _searchableAttributes: ['title', 'content', 'tags', 'keyword']
  });
}
```

```typescript
// site/src/components/Search.tsx
import { InstantSearch, SearchBox, Hits } from 'react-instantsearch-dom';

export function SiteSearch() {
  return (
    <InstantSearch searchClient={searchClient} indexName="articles">
      <SearchBox 
        placeholder="Search lawn care tips..."
        className="..."
      />
      <Hits hitComponent={ArticleHit} />
    </InstantSearch>
  );
}
```

### 3.3 Search Indexing Pipeline
**Status:** TODO

```python
# Add to content_generator.py or create index_articles.py

Tasks:
- [ ] Create indexing script that runs after article approval
- [ ] Extract searchable text (strip markdown)
- [ ] Generate keyword variations and synonyms
- [ ] Index article metadata
- [ ] Set up reindexing cron job
- [ ] Add search analytics tracking
```

---

## 📋 PRIORITY 4: Infrastructure & Scaling

### 4.1 Version Control & Repository
**Status:** TODO  
**Impact:** Code safety, collaboration, deployment automation

```bash
Tasks:
- [ ] Initialize git repository
- [ ] Create comprehensive .gitignore
- [ ] Make initial commit
- [ ] Create GitHub/GitLab repository
- [ ] Set up branch protection rules
- [ ] Document branching strategy
```

**.gitignore additions:**
```
# Python
venv/
__pycache__/
*.pyc
.env

# Node
node_modules/
.next/

# Generated content (consider Git LFS)
# site/public/images/articles/*.jpg
drafts/
*.log
```

### 4.2 Deployment & CI/CD
**Status:** TODO  
**Impact:** Automated deployments, quality gates

```markdown
Tasks:
- [ ] Deploy to Vercel (initial)
- [ ] Connect lawncare.center domain
- [ ] Set up automatic deployments on push
- [ ] Create staging environment
- [ ] Add build status checks
- [ ] Implement preview deployments for PRs
```

**Vercel Configuration:**
```json
{
  "git": {
    "deploymentEnabled": {
      "main": true,
      "staging": true
    }
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_ALGOLIA_APP_ID": "@algolia_app_id",
      "ALGOLIA_ADMIN_KEY": "@algolia_admin_key"
    }
  }
}
```

### 4.3 Image Storage Strategy (Pre-Scale)
**Status:** TODO  
**Impact:** Repository size, bandwidth costs, performance

**Current:** Local git storage ✅ (OK for <500 articles)

**Migration Path:**
```markdown
Phase 1 (Now): Local storage in git
- Simple, no additional costs
- Works for first 6 months

Phase 2 (500+ articles): Cloudflare R2
- Free egress bandwidth
- Global CDN
- S3-compatible API
- ~$0.015/GB storage

Phase 3 (Scale): Image CDN
- Cloudflare Images or Imgix
- Automatic WebP conversion
- Responsive sizing
- ~$5/month for 10K transformations
```

**Migration Tasks:**
```markdown
- [ ] Set up Cloudflare R2 bucket
- [ ] Create upload script for new images
- [ ] Migrate existing images
- [ ] Update image URLs in articles
- [ ] Remove images from git history (git filter-branch)
- [ ] Update content_generator.py to upload to R2
```

### 4.4 Database Consideration (Future)
**Status:** PLANNED  
**Impact:** Analytics, user data, dynamic features

**When to Add:**
- User accounts needed
- Comments/engagement features
- A/B testing results storage
- Email subscriber management

**Recommended:** PlanetScale (MySQL), Supabase (Postgres), or Turso (SQLite edge)

---

## 📋 PRIORITY 5: Automation & Scheduling

### 5.1 Automated Content Generation
**Status:** TODO  
**Impact:** Hands-off content production

```markdown
Tasks:
- [ ] Create content generation scheduler
- [ ] Set up cron job or cloud function
- [ ] Implement keyword queue system
- [ ] Add generation limits (budget control)
- [ ] Create notification system (email/Slack)
- [ ] Build approval queue interface
- [ ] Auto-commit approved content to git
```

**Automation Options:**

**Option A: GitHub Actions (Recommended)**
```yaml
# .github/workflows/generate-content.yml
name: Generate Daily Content
on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM daily
  workflow_dispatch:  # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate articles
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python content_generator.py --count 3
      - name: Commit drafts
        run: |
          git add drafts/
          git commit -m "Auto-generated content $(date)"
          git push
```

**Option B: Railway/Render Cron**
```python
# Serverless function triggered on schedule
```

**Option C: Local Cron (Development)**
```bash
# crontab -e
0 6 * * * cd /path/to/project && ./generate_daily.sh
```

### 5.2 Content Approval Workflow
**Status:** TODO  
**Impact:** Quality control with minimal effort

```markdown
Tasks:
- [ ] Build simple approval dashboard (Next.js admin page)
- [ ] Display pending drafts with preview
- [ ] One-click approve/reject/edit
- [ ] Auto-move approved to published folder
- [ ] Trigger Vercel rebuild on approval
- [ ] Track approval metrics
```

**Simple Admin Interface:**
```typescript
// site/src/app/admin/page.tsx
// Password-protected page showing:
// - List of drafts pending review
// - Preview button for each
// - Approve/Reject buttons
// - Edit metadata modal
// - Bulk actions
```

### 5.3 Keyword Research Automation
**Status:** TODO  
**Impact:** Data-driven content strategy

```markdown
Tasks:
- [ ] Integrate Google Search Console API
- [ ] Pull trending lawn care queries
- [ ] Analyze search volume and competition
- [ ] Auto-prioritize keyword queue
- [ ] Identify content gaps
- [ ] Track keyword performance over time
```

---

## 📋 PRIORITY 6: Monetization Strategy

### 6.1 Monetization Options Analysis

| Strategy | Effort | Revenue Potential | Timeline |
|----------|--------|-------------------|----------|
| Display Ads (AdSense) | Low | $5-15 RPM | Immediate |
| Affiliate Marketing | Medium | 5-15% commission | 1-2 months |
| Sponsored Content | Medium | $50-500/post | 3-6 months |
| Digital Products | High | $20-100/sale | 3-6 months |
| Email Newsletter | Medium | Variable | 2-3 months |
| Premium Content | High | $5-20/month | 6+ months |

### 6.2 Recommended Monetization Roadmap

**Phase 1: Foundation (Month 1-2)**
```markdown
Tasks:
- [ ] Apply for Google AdSense (need 10-15 quality articles first)
- [ ] Set up affiliate accounts:
  - [ ] Amazon Associates (lawn equipment)
  - [ ] Home Depot/Lowe's affiliate programs
  - [ ] Lawn care product brands (Scotts, etc.)
- [ ] Create affiliate disclosure page
- [ ] Add privacy policy (required for ads)
- [ ] Implement cookie consent banner
```

**Phase 2: Content Monetization (Month 2-4)**
```markdown
Tasks:
- [ ] Insert contextual affiliate links in articles
- [ ] Create "Best Products" recommendation articles
- [ ] Add product comparison tables
- [ ] Implement product schema markup
- [ ] Track affiliate link clicks
- [ ] A/B test ad placements
```

**Phase 3: List Building (Month 3-5)**
```markdown
Tasks:
- [ ] Add email signup form (ConvertKit, Mailchimp free tier)
- [ ] Create lead magnet: "Seasonal Lawn Care Calendar PDF"
- [ ] Build welcome email sequence
- [ ] Send weekly lawn care tips newsletter
- [ ] Promote affiliate products in emails
- [ ] Track email conversion rates
```

**Phase 4: Premium Content (Month 6+)**
```markdown
Tasks:
- [ ] Identify high-value topics (lawn renovation, pest control)
- [ ] Create comprehensive premium guides
- [ ] Set up payment system (Gumroad, Stripe)
- [ ] Build membership area (optional)
- [ ] Offer one-time purchase PDFs ($10-30 each)
```

### 6.3 Revenue Projections (Conservative)

**Assumptions:**
- 100 articles published
- 10,000 monthly visitors (after 6 months SEO)
- 2% click-through on affiliate links
- $8 RPM on display ads

| Month | Traffic | Ad Revenue | Affiliate | Total |
|-------|---------|------------|-----------|-------|
| 3 | 500 | $4 | $10 | $14 |
| 6 | 5,000 | $40 | $75 | $115 |
| 9 | 15,000 | $120 | $225 | $345 |
| 12 | 30,000 | $240 | $450 | $690 |

**Break-even:** ~Month 4-5 (covering $15/month costs)

### 6.4 Monetization Implementation Tasks

```markdown
Priority Tasks:
- [ ] Create /privacy-policy page
- [ ] Create /affiliate-disclosure page
- [ ] Create /terms-of-service page
- [ ] Add footer links to legal pages
- [ ] Sign up for Amazon Associates
- [ ] Apply for Google AdSense
- [ ] Integrate ad code into site layout
- [ ] Set up Google Analytics 4
- [ ] Create conversion tracking events
- [ ] Build "Recommended Products" component
```

**Affiliate Link Component:**
```typescript
// site/src/components/ProductRecommendation.tsx
export function ProductCard({ 
  name, 
  description, 
  affiliateUrl, 
  imageUrl 
}: ProductProps) {
  return (
    <div className="border rounded-lg p-4 bg-green-50">
      <img src={imageUrl} alt={name} />
      <h4>{name}</h4>
      <p>{description}</p>
      <a 
        href={affiliateUrl} 
        target="_blank" 
        rel="noopener sponsored"
        className="btn-primary"
      >
        Check Price on Amazon
      </a>
      <small className="text-gray-500">
        (Affiliate link - we may earn a commission)
      </small>
    </div>
  );
}
```

---

## 📋 PRIORITY 7: SEO & Performance

### 7.1 Technical SEO
**Status:** TODO  
**Impact:** Search rankings, organic traffic

```markdown
Tasks:
- [ ] Generate XML sitemap automatically
- [ ] Create robots.txt
- [ ] Add canonical URLs
- [ ] Implement Open Graph meta tags
- [ ] Add Twitter Card meta tags
- [ ] Create JSON-LD structured data (Article schema)
- [ ] Submit sitemap to Google Search Console
- [ ] Submit sitemap to Bing Webmaster Tools
- [ ] Verify site ownership in GSC
- [ ] Monitor Core Web Vitals
```

**Schema.org Article Markup:**
```typescript
const articleSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": article.title,
  "description": article.meta_description,
  "image": article.featured_image,
  "datePublished": article.generated_at,
  "author": {
    "@type": "Organization",
    "name": "Lawn Care Center"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Lawn Care Center",
    "logo": {
      "@type": "ImageObject",
      "url": "https://lawncare.center/logo.png"
    }
  }
};
```

### 7.2 Performance Optimization
**Status:** TODO  
**Impact:** User experience, SEO rankings

```markdown
Tasks:
- [ ] Implement Next.js Image optimization
- [ ] Enable static page generation (SSG)
- [ ] Add caching headers
- [ ] Minimize JavaScript bundle
- [ ] Implement lazy loading for images
- [ ] Add blur placeholder for images
- [ ] Compress all assets
- [ ] Set up CDN (Vercel Edge Network)
- [ ] Monitor with PageSpeed Insights
- [ ] Target: 90+ score on mobile
```

### 7.3 Analytics & Tracking
**Status:** TODO  
**Impact:** Data-driven decisions

```markdown
Tasks:
- [ ] Set up Google Analytics 4
- [ ] Configure conversion events
- [ ] Track article engagement (scroll depth, time on page)
- [ ] Set up Google Search Console
- [ ] Monitor keyword rankings
- [ ] Track affiliate link clicks
- [ ] Create analytics dashboard
- [ ] Weekly performance reports
```

---

## 📋 PRIORITY 8: Content Strategy Enhancements

### 8.1 Internal Linking System
**Status:** TODO  
**Impact:** SEO, user engagement, reduced bounce rate

```markdown
Tasks:
- [ ] Build related articles component
- [ ] Auto-suggest internal links during generation
- [ ] Create topic clusters (pillar + supporting articles)
- [ ] Implement breadcrumb navigation
- [ ] Add "You might also like" section
- [ ] Track internal link clicks
```

### 8.2 Content Freshness
**Status:** TODO  
**Impact:** SEO rankings, accuracy

```markdown
Tasks:
- [ ] Add "last updated" date to frontmatter
- [ ] Create content refresh schedule
- [ ] Identify outdated articles automatically
- [ ] Track seasonal content for yearly updates
- [ ] Version control for article revisions
```

### 8.3 User Engagement Features
**Status:** TODO  
**Impact:** Time on site, return visitors

```markdown
Tasks:
- [ ] Add estimated read time (already have)
- [ ] Implement progress bar while reading
- [ ] Add social sharing buttons
- [ ] Create print-friendly version
- [ ] Add "save for later" bookmark feature
- [ ] Enable article comments (later phase)
```

---

## 🚀 IMMEDIATE ACTION ITEMS (Next 7 Days)

### ✅ COMPLETED TODAY (Nov 15)
- [x] Integrate DALL-E 3 API
- [x] Build smart prompt engineering system
- [x] Update Next.js to display hero images
- [x] Add image optimization
- [x] Update all documentation
- [x] Test image generation (1 article)
- [x] Dev server working

### Day 1-2: Content Generation & Deploy (NEXT STEPS)
- [ ] Generate 10-15 articles to populate homepage
- [ ] Review and approve generated articles
- [ ] Move approved articles to site/content/posts/
- [ ] Initialize git repository and make initial commit
- [ ] Deploy to Vercel with content
- [ ] Connect lawncare.center domain

### Day 3-4: Image Enhancement (Optional)
- [ ] Update image prompts for enhanced photorealism
- [ ] Implement mid-article section images (second image)
- [ ] Add comprehensive image SEO (title, caption, structured data)
- [ ] Test multiple image variations

### Day 5-6: Voice & Content Refinement
- [ ] Create voice_config.json structure
- [ ] **WAITING:** Receive writing samples from user
- [ ] Adjust article length to 800-1000 words (if desired)
- [ ] Generate sample articles with new voice

### Day 7: Monetization Prep
- [ ] Create privacy policy page
- [ ] Create affiliate disclosure page
- [ ] Sign up for Amazon Associates
- [ ] Add legal footer links

---

## 📝 NOTES FOR CLAUDE CODE

### Execution Priority
1. Complete foundation (git, deploy, domain)
2. Enhance images (photorealism, dual images, SEO)
3. Implement voice customization
4. Add search functionality
5. Set up monetization infrastructure
6. Automate content pipeline
7. Optimize performance

### Important Constraints
- Budget: $10-20/month maximum
- Preference: Free tier services where possible
- MVP first, scale later
- Human review initially, full automation later
- Focus on SEO and organic traffic
- Local image storage until 500+ articles

### Key Files to Modify
1. `content_generator.py` - Core generation logic
2. `site/src/lib/posts.ts` - Content loading
3. `site/src/app/page.tsx` - Homepage
4. `site/src/app/articles/[slug]/page.tsx` - Article pages
5. `.env` - API keys
6. `requirements.txt` - Python dependencies
7. `site/package.json` - Node dependencies

### Testing Commands
```bash
# Generate content
source venv/bin/activate
python content_generator.py --count 1

# Build site
cd site && npm run build

# Run locally
npm run dev

# Deploy
npx vercel --prod
```

---

## 📊 SUCCESS METRICS

### Short-term (3 months)
- [ ] 50+ published articles
- [ ] Site live and indexed
- [ ] Search functionality working
- [ ] First affiliate revenue
- [ ] Google AdSense approved

### Medium-term (6 months)
- [ ] 150+ published articles
- [ ] 5,000+ monthly visitors
- [ ] $100+/month revenue
- [ ] Email list: 500+ subscribers
- [ ] Top 10 rankings for 10+ keywords

### Long-term (12 months)
- [ ] 300+ published articles
- [ ] 30,000+ monthly visitors
- [ ] $500+/month revenue
- [ ] Fully automated pipeline
- [ ] Authority site status

---

## ❓ QUESTIONS FOR USER

1. **Writing Samples:** Can you provide 3-5 paragraphs in your desired voice/tone?

2. **Search Priority:** Is NLP search critical for MVP, or can it wait until 50+ articles?

3. **Image Storage Budget:** OK with images in git for now, or prefer R2 immediately?

4. **Monetization Preference:** Display ads first, or pure affiliate marketing?

5. **Content Schedule:** How many articles per day/week is sustainable for review?

6. **Domain Timeline:** Is lawncare.center DNS accessible, or need help with Hostinger setup?

---

*This TODO list is designed for Claude Code to execute tasks systematically. Update status as tasks complete.*

**Last Updated:** November 15, 2025 (DALL-E 3 implementation complete)
**Next Review:** November 22, 2025

---

## 📌 SUMMARY OF TODAY'S ACCOMPLISHMENTS

### What We Built (Nov 15, 2025):
1. **DALL-E 3 Integration** - Full implementation with OpenAI API
2. **Smart Prompt Engineering** - Keyword-based image generation (aeration, mowing, watering, etc.)
3. **Seasonal Variations** - Different lighting for spring, summer, fall, winter
4. **Image Optimization** - Automatic JPEG compression to ~500KB
5. **Frontend Display** - Hero images on homepage and article pages with hover effects
6. **SEO Alt Text** - Automatic generation for accessibility
7. **Documentation** - Updated README, created IMPLEMENTATION_COMPLETE.md
8. **Environment Setup** - Added .env support with OpenAI API key
9. **Testing** - Successfully generated 1 test article with hero image

### What's Working:
- Content generator creates articles with hero images
- Images display beautifully on homepage and article pages
- Fallback system if image generation fails
- Dev server running at localhost:3001
- Cost: ~$0.10-0.13 per article (text + image)

### Next Immediate Steps:
1. Generate 10-15 articles to populate site
2. Deploy to Vercel
3. Connect domain
4. Start monetization setup
