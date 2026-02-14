# Lawn Care Content Engine - Master TODO List v2

**Project:** lawncare.center Automated Content System  
**Purpose:** Task list for Claude Code to execute  
**Created:** November 15, 2025  
**Updated:** November 15, 2025  
**Goal:** Fully automated, monetizable lawn care content site

---

## 🔑 CRITICAL CONFIGURATION

### Amazon Affiliate Tag
```
AMAZON_AFFILIATE_TAG = "amazonlinkp00-20"
```

Add to `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
AMAZON_AFFILIATE_TAG=amazonlinkp00-20
```

Usage in Python:
```python
import os
AFFILIATE_TAG = os.getenv('AMAZON_AFFILIATE_TAG', 'amazonlinkp00-20')

def build_affiliate_url(search_term):
    encoded = search_term.replace(' ', '+')
    return f"https://www.amazon.com/s?k={encoded}&tag={AFFILIATE_TAG}"
```

---

## 📦 PRODUCT SOURCING STRATEGY

### How to Source Products for Affiliate Links

**Method 1: Curated Product Database (Recommended)**

Create `products/lawn_care_products.json`:
```json
{
  "products": [
    {
      "category": "aerators",
      "items": [
        {
          "name": "manual core aerator",
          "keywords": ["core aerator", "aerator", "lawn aerator"],
          "amazon_search": "manual core aerator lawn",
          "asin": "B07GBFKD4K",
          "price_range": "$30-60",
          "rating": "4.5+",
          "best_for": "small to medium lawns"
        },
        {
          "name": "spike aerator shoes",
          "keywords": ["aerator shoes", "spike aerator"],
          "amazon_search": "lawn aerator shoes spikes",
          "asin": "B07RNQZQX9",
          "price_range": "$20-35",
          "rating": "4.0+",
          "best_for": "budget option"
        }
      ]
    },
    {
      "category": "fertilizers",
      "items": [
        {
          "name": "Scotts Turf Builder",
          "keywords": ["lawn fertilizer", "turf builder", "scotts"],
          "amazon_search": "scotts turf builder lawn fertilizer",
          "asin": "B00B04KB8Q",
          "price_range": "$25-45",
          "rating": "4.5+",
          "best_for": "general lawn feeding"
        },
        {
          "name": "Milorganite organic fertilizer",
          "keywords": ["organic fertilizer", "milorganite", "slow release"],
          "amazon_search": "milorganite organic nitrogen fertilizer",
          "asin": "B00GTDI4LG",
          "price_range": "$30-40",
          "rating": "4.7+",
          "best_for": "organic lawn care"
        }
      ]
    },
    {
      "category": "spreaders",
      "items": [
        {
          "name": "broadcast spreader",
          "keywords": ["spreader", "broadcast spreader", "fertilizer spreader"],
          "amazon_search": "broadcast spreader lawn fertilizer",
          "asin": "B00K2FG92W",
          "price_range": "$50-120",
          "rating": "4.3+",
          "best_for": "medium to large lawns"
        },
        {
          "name": "handheld spreader",
          "keywords": ["hand spreader", "handheld spreader"],
          "amazon_search": "handheld lawn spreader seed fertilizer",
          "asin": "B00004RA0M",
          "price_range": "$15-30",
          "rating": "4.4+",
          "best_for": "small lawns and spot treatment"
        }
      ]
    },
    {
      "category": "weed_control",
      "items": [
        {
          "name": "pre-emergent herbicide",
          "keywords": ["pre-emergent", "crabgrass preventer", "weed preventer"],
          "amazon_search": "pre emergent herbicide crabgrass",
          "asin": "B00GZLM0S2",
          "price_range": "$25-50",
          "rating": "4.5+",
          "best_for": "spring weed prevention"
        },
        {
          "name": "selective weed killer",
          "keywords": ["weed killer", "herbicide", "broadleaf killer"],
          "amazon_search": "selective lawn weed killer broadleaf",
          "asin": "B00JSIVBMS",
          "price_range": "$20-40",
          "rating": "4.3+",
          "best_for": "targeting specific weeds"
        }
      ]
    },
    {
      "category": "grass_seed",
      "items": [
        {
          "name": "Kentucky Bluegrass seed",
          "keywords": ["grass seed", "bluegrass", "kentucky bluegrass"],
          "amazon_search": "kentucky bluegrass seed lawn",
          "asin": "B07CZ3DVBR",
          "price_range": "$30-80",
          "rating": "4.4+",
          "best_for": "cool season lawns"
        },
        {
          "name": "perennial ryegrass seed",
          "keywords": ["ryegrass", "perennial ryegrass", "overseeding"],
          "amazon_search": "perennial ryegrass seed overseeding",
          "asin": "B074C9KZFK",
          "price_range": "$25-60",
          "rating": "4.5+",
          "best_for": "quick germination overseeding"
        }
      ]
    },
    {
      "category": "soil_testing",
      "items": [
        {
          "name": "soil test kit",
          "keywords": ["soil test", "ph test", "soil testing kit"],
          "amazon_search": "soil test kit lawn garden ph",
          "asin": "B00SWKOH6E",
          "price_range": "$15-30",
          "rating": "4.3+",
          "best_for": "DIY soil analysis"
        },
        {
          "name": "soil pH meter",
          "keywords": ["ph meter", "soil meter", "moisture meter"],
          "amazon_search": "soil ph meter moisture light tester",
          "asin": "B07BR52P26",
          "price_range": "$10-20",
          "rating": "4.2+",
          "best_for": "quick pH readings"
        }
      ]
    },
    {
      "category": "lawn_tools",
      "items": [
        {
          "name": "dethatching rake",
          "keywords": ["dethatcher", "thatch rake", "dethatching"],
          "amazon_search": "dethatching rake lawn thatch",
          "asin": "B0007XZQNU",
          "price_range": "$30-50",
          "rating": "4.4+",
          "best_for": "manual thatch removal"
        },
        {
          "name": "lawn edger",
          "keywords": ["edger", "lawn edger", "edge trimmer"],
          "amazon_search": "lawn edger manual steel",
          "asin": "B00004RBDK",
          "price_range": "$25-45",
          "rating": "4.5+",
          "best_for": "clean lawn borders"
        }
      ]
    },
    {
      "category": "watering",
      "items": [
        {
          "name": "oscillating sprinkler",
          "keywords": ["sprinkler", "oscillating sprinkler", "lawn sprinkler"],
          "amazon_search": "oscillating lawn sprinkler adjustable",
          "asin": "B00005A8Y9",
          "price_range": "$20-45",
          "rating": "4.3+",
          "best_for": "rectangular lawn coverage"
        },
        {
          "name": "sprinkler timer",
          "keywords": ["watering timer", "hose timer", "irrigation timer"],
          "amazon_search": "garden hose water timer programmable",
          "asin": "B07GRMQDVQ",
          "price_range": "$25-50",
          "rating": "4.4+",
          "best_for": "automated watering schedule"
        }
      ]
    }
  ]
}
```

**Method 2: AI-Powered Product Detection**

Claude scans article content and matches to curated database:
```python
def find_product_opportunities(content, product_db):
    """
    1. Scan content for product keywords
    2. Match to curated product database
    3. Return best product match with affiliate URL
    """
    for category in product_db['products']:
        for product in category['items']:
            for keyword in product['keywords']:
                if keyword.lower() in content.lower():
                    return {
                        'product': product['name'],
                        'url': build_affiliate_url(product['amazon_search']),
                        'context': keyword
                    }
```

**Method 3: Dynamic Amazon Search URLs**

For products not in database, generate search URLs:
```python
def build_affiliate_url(search_term):
    """
    Creates Amazon search URL with affiliate tag.
    User sees search results, you get commission on any purchase.
    """
    encoded = search_term.replace(' ', '+')
    return f"https://www.amazon.com/s?k={encoded}&tag=amazonlinkp00-20"

# Example outputs:
# "core aerator" → https://www.amazon.com/s?k=core+aerator&tag=amazonlinkp00-20
# "lawn fertilizer" → https://www.amazon.com/s?k=lawn+fertilizer&tag=amazonlinkp00-20
```

**Method 4: Direct ASIN Links (Highest Conversion)**

For specific products with known ASINs:
```python
def build_direct_product_url(asin):
    """
    Links directly to specific product page.
    Higher conversion but requires product research.
    """
    return f"https://www.amazon.com/dp/{asin}?tag=amazonlinkp00-20"

# Example:
# Scotts Turf Builder → https://www.amazon.com/dp/B00B04KB8Q?tag=amazonlinkp00-20
```

---

## ✅ AFFILIATE LINK BEST PRACTICES

### FTC Compliance (Required)
- [ ] Add disclosure at top of every article with affiliate links
- [ ] Create `/affiliate-disclosure` page
- [ ] Use clear language: "As an Amazon Associate, I earn from qualifying purchases"
- [ ] Disclosure must be conspicuous (not hidden in footer)

**Article Disclosure Format:**
```markdown
*This article contains affiliate links. If you purchase through these links, 
we may earn a small commission at no extra cost to you. 
[Learn more](/affiliate-disclosure)*
```

### Link Placement Rules
1. **Maximum 3-5 affiliate links per article** - Avoid appearing spammy
2. **First mention only** - Don't link every occurrence of "lawn mower"
3. **Contextually relevant** - Only link when product genuinely helps reader
4. **Natural anchor text** - "core aerator" not "CLICK HERE FOR DEALS"
5. **No misleading claims** - Don't guarantee results or fake reviews

### High-Converting Strategies
1. **Product mentions in how-to steps:**
   ```markdown
   "Step 3: Using your [broadcast spreader](affiliate-url), apply fertilizer..."
   ```

2. **Tool recommendations:**
   ```markdown
   "For this job, you'll need a [quality dethatching rake](affiliate-url)..."
   ```

3. **Product comparison callouts:**
   ```markdown
   "While manual aerators work great for small lawns, consider a 
   [powered core aerator](affiliate-url) for properties over 5,000 sq ft."
   ```

4. **"Best Products" sections:**
   ```markdown
   ## Recommended Products
   - **[Scotts Turf Builder](url)** - Best overall lawn fertilizer
   - **[Milorganite](url)** - Best organic option
   ```

### What NOT to Do
- ❌ Link every product mention (looks spammy)
- ❌ Use deceptive anchor text ("Click here for secret deal")
- ❌ Hide affiliate nature of links
- ❌ Recommend products you haven't researched
- ❌ Prioritize commission over reader value
- ❌ Link to irrelevant products
- ❌ Use link cloaking that hides affiliate nature

### Link Format Standards
```markdown
# CORRECT - Natural, contextual
"A [soil test kit](https://www.amazon.com/s?k=soil+test+kit&tag=amazonlinkp00-20) 
will help you determine your lawn's pH level."

# WRONG - Pushy, salesy
"BUY THIS AMAZING [SOIL TEST KIT NOW](url) - BEST DEAL EVER!!!"

# CORRECT - Helpful recommendation
"For aerating, I recommend a [manual core aerator](url) for lawns under 3,000 sq ft."

# WRONG - Forced link
"Your lawn (which needs [products](url)) will benefit from aeration."
```

### Tracking Performance
```python
# Add to frontmatter for each article
affiliate_links:
  - product: "core aerator"
    url: "https://www.amazon.com/s?k=core+aerator&tag=amazonlinkp00-20"
    position: "paragraph_3"
  - product: "lawn fertilizer"
    url: "https://www.amazon.com/s?k=lawn+fertilizer&tag=amazonlinkp00-20"
    position: "step_5"
  
# Track in Amazon Associates dashboard:
# - Click-through rate by product category
# - Conversion rate by article
# - Revenue per article
# - Best performing product types
```

---

## 🎯 Current State Summary

- ✅ Python content generator with Claude Sonnet 4
- ✅ DALL-E 3 hero image generation integrated
- ✅ Next.js site with Tailwind CSS
- ✅ Markdown-based content workflow
- ✅ Amazon Associates account (tag: amazonlinkp00-20)
- ⏳ Not yet deployed to Vercel
- ⏳ No search functionality
- ⏳ No automated affiliate linking
- ⏳ No keyword research pipeline
- ⏳ No QA evaluation system

---

## 📋 PRIORITY 1: Foundation & Deployment (DO FIRST)

### 1.1 Version Control Setup
**Status:** TODO  
**Timeline:** Day 1  
**Impact:** Code safety, deployment automation

```bash
Tasks:
- [ ] Initialize git repository: git init
- [ ] Create comprehensive .gitignore
- [ ] Make initial commit with all current code
- [ ] Create GitHub repository
- [ ] Push to remote
- [ ] Set up branch protection (main branch)
```

**.gitignore:**
```
# Python
venv/
__pycache__/
*.pyc
.env
*.log

# Node
node_modules/
.next/
.vercel/

# Content (drafts stay local until approved)
drafts/

# OS
.DS_Store
Thumbs.db
```

### 1.2 Deploy to Vercel
**Status:** TODO  
**Timeline:** Day 1-2  
**Impact:** Site live, SEO clock starts ticking

```bash
Tasks:
- [ ] Install Vercel CLI: npm i -g vercel
- [ ] Run initial deploy: cd site && vercel
- [ ] Configure project settings
- [ ] Set environment variables in Vercel dashboard
- [ ] Test deployment URL works
- [ ] Enable automatic deployments on git push
```

### 1.3 Connect Domain
**Status:** TODO  
**Timeline:** Day 2  
**Impact:** Brand identity, SEO authority

```markdown
Tasks:
- [ ] Log into Hostinger DNS management
- [ ] Add Vercel DNS records:
  - A record: 76.76.21.21
  - CNAME: cname.vercel-dns.com
- [ ] Add domain in Vercel project settings
- [ ] Verify SSL certificate issued
- [ ] Test https://lawncare.center loads
- [ ] Set up www redirect to non-www (or vice versa)
```

### 1.4 Google Search Console Setup
**Status:** TODO  
**Timeline:** Day 2-3  
**Impact:** SEO monitoring, future keyword data

```markdown
Tasks:
- [ ] Go to search.google.com/search-console
- [ ] Add property: lawncare.center
- [ ] Verify ownership (DNS TXT record method recommended)
- [ ] Submit sitemap.xml
- [ ] Request indexing for homepage
- [ ] Set up email alerts for issues
```

**Note:** GSC data takes 2-4 weeks to accumulate. Don't wait for it - start content generation immediately.

---

## 📋 PRIORITY 2: Enhanced Image System

### 2.1 Photorealistic Image Prompts
**Status:** TODO  
**Timeline:** Day 3-4  
**Impact:** Professional appearance, higher engagement

```python
# Update DALL-E 3 prompts for maximum photorealism

Tasks:
- [ ] Modify build_image_prompt() function
- [ ] Add camera/lens specifications
- [ ] Include professional photography terms
- [ ] Add specific lighting descriptors
- [ ] Test 10 sample images, rate photorealism
- [ ] Iterate until consistently 8+/10 quality
```

**Enhanced Prompt Template:**
```python
def build_photorealistic_prompt(keyword, season):
    prompt = f"""
    Ultra-realistic photograph captured with Canon EOS R5 camera, 24-70mm f/2.8 lens.
    Subject: Beautiful residential lawn, {keyword_to_visual(keyword)}.
    
    Technical specifications:
    - Shallow depth of field, f/4 aperture
    - Natural bokeh in background
    - Rule of thirds composition
    - Shot during {season_lighting[season]}
    - Color profile: Natural with slight warmth
    - Dynamic range: HDR balanced
    
    Scene elements:
    - Well-maintained suburban home softly blurred in background
    - Professional landscaping visible
    - {seasonal_elements[season]}
    
    Style: Magazine editorial quality, National Geographic aesthetic.
    Absolute requirements: Photorealistic only, no CGI, no illustrations, 
    no text, no watermarks, no people, no artificial elements.
    """
    return prompt
```

### 2.2 Mid-Article Section Images
**Status:** TODO  
**Timeline:** Day 4-5  
**Impact:** Engagement, time on page, SEO

```python
Tasks:
- [ ] Analyze article structure to identify best section for image
- [ ] Create generate_section_image() function
- [ ] Generate contextual prompt based on section H2 content
- [ ] Insert image markdown after selected H2
- [ ] Update frontmatter schema to include section_image
- [ ] Modify Next.js renderer to display inline images
- [ ] Test with 5 articles
```

**Implementation:**
```python
def insert_section_image(article_content, keyword, slug):
    """
    Insert a contextual image in the middle of the article.
    """
    # Parse H2 sections
    sections = parse_h2_sections(article_content)
    
    # Select middle section (or most visual)
    target_section = select_best_section_for_image(sections)
    
    # Generate section-specific image
    section_prompt = build_section_image_prompt(
        target_section['title'],
        target_section['content'],
        keyword
    )
    
    # Generate image (1024x1024 square for inline)
    image_path = generate_dalle_image(
        section_prompt,
        f"{slug}-section",
        size="1024x1024"
    )
    
    # Insert markdown image after H2
    image_markdown = f"\n\n![{target_section['title']}]({image_path})\n*{generate_caption(target_section)}*\n\n"
    
    modified_content = insert_after_h2(
        article_content,
        target_section['title'],
        image_markdown
    )
    
    return modified_content, image_path
```

### 2.3 Comprehensive Image SEO
**Status:** TODO  
**Timeline:** Day 5-6  
**Impact:** Image search traffic, accessibility, Core Web Vitals

```markdown
Tasks:
- [ ] Generate keyword-rich alt text (max 125 chars)
- [ ] Create descriptive title attributes
- [ ] Add image captions for display
- [ ] Implement Schema.org ImageObject markup
- [ ] Create image sitemap (sitemap-images.xml)
- [ ] Optimize file naming: {keyword-slug}-{type}.jpg
- [ ] Add lazy loading with blur placeholders
- [ ] Implement WebP conversion (Next.js Image component)
```

**Updated Frontmatter:**
```yaml
images:
  hero:
    src: "/images/articles/how-aerate-lawn-hero.jpg"
    alt: "Professional lawn aeration showing soil plugs on healthy green residential grass"
    title: "Lawn Aeration Process"
    caption: "Core aeration removes soil plugs to improve drainage and root growth"
  section:
    src: "/images/articles/how-aerate-lawn-tools.jpg"
    alt: "Manual core aerator tool penetrating lawn soil"
    title: "Core Aerator Equipment"
    caption: "Manual aerators work well for small to medium lawns"
```

---

## 📋 PRIORITY 3: Content Quality Improvements

### 3.1 Shorter, High-Impact Articles
**Status:** TODO  
**Timeline:** Day 6-7  
**Impact:** Better readability, faster generation, lower costs

```markdown
Tasks:
- [ ] Reduce target word count: 1400-1600 → 800-1000 words
- [ ] Update Claude system prompt for conciseness
- [ ] Add "Quick Answer" box at article top
- [ ] Include "Key Takeaways" bullet summary
- [ ] Focus on actionable steps over background
- [ ] Test Flesch-Kincaid readability (target: Grade 8)
- [ ] Generate 5 sample articles with new format
```

**New Article Structure:**
```markdown
# [Title - Question Format]

**Quick Answer:** [2-3 sentence direct answer]

**Key Takeaways:**
- Actionable point 1
- Actionable point 2  
- Actionable point 3

## Understanding [Topic]
[150-200 words - context]

[HERO IMAGE]

## Step-by-Step Guide
[300-350 words - numbered steps]

[SECTION IMAGE]

## Common Mistakes
[100-150 words - what to avoid]

## When to Call a Professional
[50-100 words - know your limits]

---
Total: 800-1000 words
Cost savings: ~30% less tokens
```

### 3.2 Voice & Tone Configuration
**Status:** WAITING FOR USER INPUT  
**Timeline:** Day 7-8  
**Impact:** Brand consistency, reader trust

```markdown
Tasks:
- [ ] Receive 3-5 writing samples from user
- [ ] Analyze samples for voice characteristics
- [ ] Create voice_config.json
- [ ] Build system prompt that enforces voice
- [ ] Test generation with voice parameters
- [ ] Iterate based on user feedback
```

**Voice Config Structure:**
```json
{
  "brand_voice": {
    "personality": "friendly expert neighbor",
    "tone": "conversational but knowledgeable",
    "formality": 3,
    "humor": 2,
    "empathy": 4,
    
    "vocabulary": {
      "use": ["here's the deal", "pro tip", "trust me"],
      "avoid": ["utilize", "leverage", "optimal"]
    },
    
    "patterns": {
      "contractions": true,
      "rhetorical_questions": true,
      "direct_address": true,
      "sentence_length": "varied, 12-20 words avg"
    },
    
    "sample_phrases": [
      "Your lawn will thank you",
      "Here's what actually works",
      "Let me break this down"
    ]
  }
}
```

**NEED FROM USER:**
> Please provide 3-5 paragraphs written in your desired voice. Could be:
> - How you'd explain lawn care to a neighbor
> - An email you've written explaining something technical
> - A sample paragraph about fall lawn prep in YOUR voice

### 3.3 Article Quality Assurance & Self-Improvement System
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Higher quality content, reduced manual editing, self-improving system  
**Additional Cost:** ~$0.05-0.08 per article (~$5-8/month for 100 articles)

```markdown
Tasks:
- [ ] Create article_qa.py evaluation system
- [ ] Build multi-dimensional scoring (Accuracy, SEO, Impact, Voice)
- [ ] Implement automatic refinement loop (max 2 rounds)
- [ ] Create feedback logging system (feedback_log.json)
- [ ] Build pattern analyzer for common issues
- [ ] Generate weekly insights report
- [ ] Auto-update generation prompts based on patterns
- [ ] Integrate QA into main content pipeline
```

**System Components:**

**1. Article Evaluator (Claude-powered):**
```python
def evaluate_article(content, keyword, title, meta_description):
    """
    Score article on:
    - Accuracy (factual correctness, completeness)
    - SEO (keyword usage, structure, meta tags)
    - Impact (actionability, readability, engagement)
    - Voice (tone consistency, brand alignment)
    
    Returns: Scores (1-10) + specific issues + priority fixes
    """
```

**2. Automatic Refinement:**
```python
def refine_article(content, evaluation):
    """
    Apply targeted fixes based on evaluation feedback.
    - Fix factual errors
    - Improve SEO elements
    - Enhance actionability
    - Adjust tone/voice
    
    Max 2 refinement rounds to control costs
    """
```

**3. Feedback Logger:**
```python
def log_feedback(article_slug, evaluation):
    """
    Track all issues found across articles:
    - Issue type and frequency
    - Category (accuracy/seo/impact/voice)
    - Specific problem patterns
    
    Builds dataset for pattern analysis
    """
```

**4. Pattern Analyzer (Weekly):**
```python
def analyze_common_issues():
    """
    Identify recurring problems:
    - "68% of articles missing Quick Answer box"
    - "42% have keyword density issues"
    - "36% too vague on measurements"
    
    Generates prompt improvements automatically
    """
```

**5. Self-Improving Prompts:**
```python
def update_generation_prompts(analysis):
    """
    Based on patterns, add rules to generation prompt:
    - "REQUIRED: Start with Quick Answer box"
    - "Include specific numbers and timing"
    - "Use keyword in first paragraph"
    
    System learns and improves over time
    """
```

**Quality Thresholds:**
```python
QUALITY_THRESHOLDS = {
    'accuracy': 8.0,      # Out of 10
    'seo_score': 8.0,     # Out of 10
    'impact_score': 7.5,  # Out of 10
    'overall': 8.0        # Weighted average
}

# If score < threshold, auto-refine (max 2 rounds)
# If still below after 2 rounds, flag for human review
```

**Cost Analysis:**
```
Per Article:
- Evaluation call: $0.02-0.03
- Refinement (40% of articles): $0.03-0.05
- Average additional cost: $0.05-0.08/article

For 100 articles/month:
- Additional cost: $5-8/month
- Time saved on manual editing: 2-3 hours
- Quality improvement: +15-25% SEO scores
- ROI: Positive (better content = more traffic = more revenue)
```

**Weekly Insights Output:**
```
📊 WEEKLY CONTENT QUALITY INSIGHTS
============================================================
Articles Analyzed: 47
Average Initial Score: 7.2/10
Refinement Rate: 38.3%

🚨 TOP ISSUES:
1. [CRITICAL] 68% missing Quick Answer box
2. [HIGH] 42% keyword not in first paragraph
3. [HIGH] 36% too vague on measurements
4. [MEDIUM] 23% tone too formal

✨ AUTO-GENERATED PROMPT FIXES:
• "REQUIRED: Begin with **Quick Answer:** box"
• "Include keyword in first 100 words"
• "Use specific numbers (e.g., '2-3 inches' not 'a few inches')"
============================================================
```

**Integration with Pipeline:**
```python
def generate_article_with_qa(keyword):
    # 1. Get enhanced prompt (with learned improvements)
    prompt = get_enhanced_generation_prompt()
    
    # 2. Generate article
    article = generate_article(keyword, prompt)
    
    # 3. Generate images
    article = add_images(article)
    
    # 4. Run QA pipeline (evaluate + refine if needed)
    article = quality_assurance_pipeline(article)
    
    # 5. Add affiliate links
    article = insert_affiliate_links(article)
    
    # 6. Save with QA metadata
    save_article(article)
    
    return article
```

**Commands:**
```bash
# Generate with QA
python content_generator.py --count 3 --with-qa

# Run weekly analysis
python article_qa.py --analyze

# Test QA on specific article
python article_qa.py --test drafts/my-article.md
```

---

## 📋 PRIORITY 4: Keyword Research Pipeline (Phased Approach)

### 4.1 Phase 1: Curated Keyword Database (NOW)
**Status:** TODO  
**Timeline:** Day 8-10  
**Impact:** Data-driven content from day one  
**Requires:** Nothing - works immediately

```python
Tasks:
- [ ] Create keywords_database.json with 100+ researched keywords
- [ ] Organize by season, intent, and difficulty
- [ ] Include search volume estimates (from free tools)
- [ ] Add keyword variations and long-tail versions
- [ ] Prioritize question-based keywords
- [ ] Build keyword selector that rotates through list
- [ ] Track which keywords have been used
```

**Keyword Database Structure:**
```json
{
  "keywords": [
    {
      "primary": "how often should i aerate my lawn",
      "variations": [
        "lawn aeration frequency",
        "how many times aerate lawn per year",
        "when to aerate lawn"
      ],
      "season": "fall",
      "intent": "informational",
      "difficulty": "medium",
      "search_volume_estimate": "1000-5000/month",
      "priority": 1,
      "used": false,
      "article_slug": null
    }
  ]
}
```

**100+ Starter Keywords (Research Done):**
```python
CURATED_KEYWORDS = {
    "spring": [
        "when to start mowing lawn in spring",
        "how to repair lawn after winter damage",
        "best time to apply pre-emergent herbicide",
        "spring lawn fertilizer schedule",
        "when to dethatch lawn in spring",
        "how to fix bare spots in lawn spring",
        "spring lawn care checklist",
        "when to overseed lawn in spring",
        "how to prevent crabgrass in spring",
        "best grass seed for spring planting"
    ],
    "summer": [
        "how often to water lawn in summer",
        "best time of day to water lawn",
        "why is my lawn turning brown in summer",
        "how to fix brown patches in lawn",
        "lawn care during drought",
        "how to keep lawn green in hot weather",
        "summer lawn fertilizer tips",
        "how to get rid of grubs in lawn",
        "lawn fungus treatment summer",
        "how to mow lawn in extreme heat"
    ],
    "fall": [
        "when to aerate lawn in fall",
        "fall lawn fertilizer application",
        "best time to overseed lawn",
        "when to stop mowing before winter",
        "how to prepare lawn for winter",
        "fall lawn care schedule",
        "should i fertilize lawn in november",
        "how to remove leaves from lawn",
        "fall weed control for lawns",
        "when to apply winterizer fertilizer"
    ],
    "winter": [
        "winter lawn care tips",
        "how to protect lawn from snow",
        "snow mold prevention lawn",
        "should i walk on frozen lawn",
        "winter lawn fertilizer",
        "when to start spring lawn care",
        "how to prepare lawn mower for winter",
        "ice melt safe for grass",
        "winter lawn disease prevention",
        "planning spring lawn renovation"
    ],
    "evergreen": [
        "how to make lawn thicker",
        "best lawn mower for small yard",
        "how to level bumpy lawn",
        "lawn care for beginners",
        "how to test soil ph for lawn",
        "best grass type for shade",
        "how to edge lawn like a pro",
        "lawn striping techniques",
        "organic lawn care guide",
        "how to fix compacted soil lawn"
    ]
}
```

### 4.2 Phase 2: Google Trends Integration (Week 2)
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Seasonal timing optimization  
**Requires:** Nothing - free API

```python
Tasks:
- [ ] Install pytrends: pip install pytrends
- [ ] Create trends_analyzer.py
- [ ] Query seasonal lawn care trends
- [ ] Identify peak interest windows
- [ ] Auto-prioritize keywords based on trending
- [ ] Schedule content for peak search periods
```

**Implementation:**
```python
# trends_analyzer.py
from pytrends.request import TrendReq
import json

def get_trending_lawn_topics():
    """
    Find what lawn care topics are trending right now.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Compare seasonal activities
    keywords = [
        'lawn aeration',
        'fall fertilizer', 
        'winterize lawn',
        'overseed lawn',
        'leaf removal'
    ]
    
    pytrends.build_payload(keywords, timeframe='today 3-m', geo='US')
    trends = pytrends.interest_over_time()
    
    # Find which keyword is peaking now
    current_trends = trends.iloc[-1].drop('isPartial')
    hottest = current_trends.idxmax()
    
    return {
        'trending_now': hottest,
        'trend_score': int(current_trends[hottest]),
        'all_scores': current_trends.to_dict()
    }


def get_seasonal_timing(keyword):
    """
    When does this keyword peak in search interest?
    """
    pytrends = TrendReq()
    pytrends.build_payload([keyword], timeframe='today 12-m', geo='US')
    
    trends = pytrends.interest_over_time()
    peak_date = trends[keyword].idxmax()
    
    return {
        'keyword': keyword,
        'peak_month': peak_date.strftime('%B'),
        'peak_week': peak_date.strftime('%Y-%m-%d'),
        'recommendation': f"Publish 2-3 weeks before {peak_date.strftime('%B %d')}"
    }


def prioritize_keywords_by_trends(keyword_list):
    """
    Reorder keywords based on current trending interest.
    """
    pytrends = TrendReq()
    
    prioritized = []
    for keyword in keyword_list:
        pytrends.build_payload([keyword], timeframe='now 7-d', geo='US')
        interest = pytrends.interest_over_time()
        
        if not interest.empty:
            avg_interest = interest[keyword].mean()
            prioritized.append({
                'keyword': keyword,
                'trend_score': avg_interest
            })
    
    return sorted(prioritized, key=lambda x: x['trend_score'], reverse=True)
```

### 4.3 Phase 3: People Also Ask Scraper (Week 2-3)
**Status:** TODO  
**Timeline:** Week 2-3  
**Impact:** Real questions people search  
**Requires:** Web scraping or free API

```python
Tasks:
- [ ] Create paa_scraper.py
- [ ] Build Google autocomplete scraper
- [ ] Integrate AlsoAsked.com API (free tier)
- [ ] Generate question variations automatically
- [ ] Feed questions into keyword database
- [ ] Prioritize by search intent
```

**Implementation:**
```python
# paa_scraper.py
import requests
from bs4 import BeautifulSoup

def get_google_autocomplete(seed_keyword):
    """
    Get Google's autocomplete suggestions.
    These are real searches people make.
    """
    url = f"http://suggestqueries.google.com/complete/search"
    params = {
        'client': 'firefox',
        'q': seed_keyword
    }
    
    response = requests.get(url, params=params)
    suggestions = response.json()[1]
    
    return suggestions


def generate_question_variations(topic):
    """
    Generate question-based keywords from a topic.
    """
    question_starters = [
        "how to", "how often", "when to", "what is the best",
        "why is my", "should i", "can i", "how long",
        "what causes", "how do i fix"
    ]
    
    variations = []
    for starter in question_starters:
        query = f"{starter} {topic}"
        autocomplete = get_google_autocomplete(query)
        variations.extend(autocomplete)
    
    return list(set(variations))


def get_related_searches(keyword):
    """
    Scrape "Related searches" from Google results.
    """
    # Note: Respect robots.txt and rate limits
    # Consider using SerpAPI free tier for production
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    related = []
    for div in soup.find_all('div', class_='related-question-pair'):
        question = div.get_text()
        related.append(question)
    
    return related
```

### 4.4 Phase 4: GSC Integration (Month 2-3)
**Status:** PLANNED (NOT NOW)  
**Timeline:** After 30+ indexed articles, 2-4 weeks of data  
**Impact:** Performance-based optimization  
**Requires:** Real traffic data

```markdown
Prerequisites (must have before implementing):
- [ ] 30+ articles published and indexed
- [ ] Site verified in Google Search Console
- [ ] 2-4 weeks of impression/click data
- [ ] At least 1,000 total impressions
- [ ] Google Cloud project with Search Console API enabled
```

**When Ready, Implement:**
```python
# gsc_analyzer.py - ONLY BUILD WHEN PREREQUISITES MET

Tasks:
- [ ] Set up Google Cloud project
- [ ] Enable Search Console API
- [ ] Create service account credentials
- [ ] Build opportunity finder (page 2-3 rankings)
- [ ] Identify content gaps
- [ ] Find high-impression, low-click keywords (title optimization)
- [ ] Automated weekly reports
- [ ] Content refresh recommendations
```

**Opportunity Finder (Future):**
```python
def find_quick_win_keywords():
    """
    Keywords ranking #11-30 (page 2-3) with good impressions.
    These are "almost there" opportunities.
    """
    # Requires real GSC data
    
    service = get_gsc_service()
    
    response = service.searchanalytics().query(
        siteUrl='https://lawncare.center',
        body={
            'startDate': '30daysAgo',
            'endDate': 'today',
            'dimensions': ['query', 'page'],
            'rowLimit': 1000
        }
    ).execute()
    
    opportunities = []
    for row in response.get('rows', []):
        position = row['position']
        impressions = row['impressions']
        
        # Page 2-3 rankings with decent impressions
        if 10 < position < 31 and impressions > 50:
            opportunities.append({
                'keyword': row['keys'][0],
                'current_page': row['keys'][1],
                'position': position,
                'impressions': impressions,
                'action': 'Create dedicated article or optimize existing'
            })
    
    return sorted(opportunities, key=lambda x: x['impressions'], reverse=True)
```

### 4.5 Keyword Pipeline Integration
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Automated, data-driven content selection

```python
Tasks:
- [ ] Create keyword_selector.py
- [ ] Integrate curated database
- [ ] Add trending score from Google Trends
- [ ] Factor in seasonal timing
- [ ] Avoid duplicate content
- [ ] Auto-update used keywords
- [ ] Generate daily content recommendations
```

**Unified Keyword Selector:**
```python
# keyword_selector.py

def select_next_keyword():
    """
    Intelligently select the next keyword to target.
    Uses multiple data sources for best decision.
    """
    # Load curated database
    with open('keywords_database.json') as f:
        database = json.load(f)
    
    # Filter unused keywords
    available = [k for k in database['keywords'] if not k['used']]
    
    # Get current season
    current_season = get_current_season()
    
    # Filter by season (prefer seasonal, include evergreen)
    seasonal = [k for k in available if k['season'] in [current_season, 'evergreen']]
    
    # Score each keyword
    scored = []
    for keyword in seasonal:
        score = 0
        
        # Priority score (user-defined importance)
        score += (10 - keyword.get('priority', 5)) * 10
        
        # Trending score (from Google Trends)
        trend_score = get_trend_score(keyword['primary'])
        score += trend_score
        
        # Seasonal timing bonus
        if is_peak_season(keyword['primary']):
            score += 25
        
        scored.append({
            'keyword': keyword['primary'],
            'score': score,
            'data': keyword
        })
    
    # Return highest scored
    best = sorted(scored, key=lambda x: x['score'], reverse=True)[0]
    
    # Mark as used
    mark_keyword_used(best['keyword'])
    
    return best['keyword']
```

---

## 📋 PRIORITY 5: Automated Affiliate Link System

### 5.1 Product Opportunity Detection
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Revenue generation, passive income

```python
Tasks:
- [ ] Create affiliate_linker.py
- [ ] Build product mention detector using Claude
- [ ] Create Amazon search URL builder with affiliate tag
- [ ] Implement smart link insertion (first mention only)
- [ ] Add product recommendation sections
- [ ] Track inserted links in frontmatter
- [ ] Limit to 3-5 links per article (avoid spam)
```

**Core Implementation:**
```python
# affiliate_linker.py

AFFILIATE_TAG = "lawncare0c-20"  # Your Amazon Associates tag

def detect_product_opportunities(article_content):
    """
    Use Claude to identify products that could have affiliate links.
    """
    prompt = f"""
    Analyze this lawn care article and identify specific products/tools mentioned.
    
    Article: {article_content}
    
    Return JSON array:
    [
      {{
        "product": "core aerator",
        "amazon_search": "lawn core aerator manual",
        "link_text": "core aerator",
        "position": "inline"
      }}
    ]
    
    Rules:
    - Max 5 products per article
    - Only products available on Amazon
    - Natural link text, not spammy
    """
    
    # Call Claude API
    response = get_claude_response(prompt)
    return json.loads(response)


def build_affiliate_url(search_term):
    """Build Amazon affiliate link."""
    encoded = search_term.replace(' ', '+')
    return f"https://www.amazon.com/s?k={encoded}&tag={AFFILIATE_TAG}"


def insert_affiliate_links(content, products):
    """Insert links naturally into article."""
    for product in products[:5]:  # Max 5
        link_text = product['link_text']
        url = build_affiliate_url(product['amazon_search'])
        
        # Replace first occurrence only
        pattern = re.compile(rf'\b({re.escape(link_text)})\b', re.IGNORECASE)
        match = pattern.search(content)
        
        if match:
            original = match.group(1)
            linked = f'[{original}]({url})'
            content = content[:match.start()] + linked + content[match.end():]
    
    return content


def add_affiliate_disclosure(content):
    """Add required FTC disclosure."""
    disclosure = "\n\n---\n*As an Amazon Associate, I earn from qualifying purchases.*\n"
    return content + disclosure
```

### 5.2 Batch Processing & Integration
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Monetize all content automatically

```markdown
Tasks:
- [ ] Add affiliate processing to content generation pipeline
- [ ] Create batch processor for existing articles
- [ ] Track affiliate link performance
- [ ] A/B test link placements
- [ ] Create product recommendation component for site
- [ ] Update legal pages (affiliate disclosure)
```

**Pipeline Integration:**
```python
def generate_article(keyword):
    # 1. Generate text content
    article = generate_with_claude(keyword)
    
    # 2. Generate images
    article['hero_image'] = generate_hero_image(keyword)
    article['section_image'] = generate_section_image(article)
    
    # 3. Add affiliate links
    article['content'] = insert_affiliate_links(article['content'])
    article['has_affiliate_links'] = True
    
    # 4. Save article
    save_article(article)
    
    return article
```

---

## 📋 PRIORITY 6: Site-Wide NLP Search

### 6.1 Search Solution Selection
**Status:** TODO  
**Timeline:** Week 3 (after 20+ articles)  
**Impact:** User experience, time on site

**Recommended: Algolia (Free Tier)**
- 10,000 searches/month free
- Typo tolerance built-in
- Fast implementation
- Great React components

```markdown
Tasks:
- [ ] Sign up for Algolia free account
- [ ] Install dependencies: npm install algoliasearch react-instantsearch
- [ ] Create search index schema
- [ ] Build article indexing script
- [ ] Implement search UI component
- [ ] Add to site header
- [ ] Configure relevance ranking
- [ ] Test with 20+ articles
```

### 6.2 Search Implementation
**Status:** TODO  
**Timeline:** Week 3  

```typescript
// site/src/lib/algolia.ts
import algoliasearch from 'algoliasearch';

const client = algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!,
  process.env.ALGOLIA_ADMIN_KEY!
);

const index = client.initIndex('lawn_articles');

export async function indexArticle(article) {
  await index.saveObject({
    objectID: article.slug,
    title: article.title,
    content: stripMarkdown(article.content),
    description: article.meta_description,
    tags: article.tags,
    keyword: article.keyword,
    season: article.season
  });
}

// Index all articles after generation
export async function reindexAll() {
  const articles = getAllArticles();
  await index.saveObjects(articles.map(formatForAlgolia));
}
```

```typescript
// site/src/components/Search.tsx
import { InstantSearch, SearchBox, Hits } from 'react-instantsearch';

export function SiteSearch() {
  return (
    <InstantSearch searchClient={searchClient} indexName="lawn_articles">
      <SearchBox 
        placeholder="Search lawn care tips..."
        classNames={{
          input: 'w-full px-4 py-2 border rounded-lg',
          submit: 'hidden',
          reset: 'hidden'
        }}
      />
      <Hits hitComponent={ArticleHit} />
    </InstantSearch>
  );
}

function ArticleHit({ hit }) {
  return (
    <a href={`/articles/${hit.slug}`} className="block p-4 hover:bg-gray-50">
      <h3 className="font-semibold">{hit.title}</h3>
      <p className="text-sm text-gray-600">{hit.description}</p>
    </a>
  );
}
```

---

## 📋 PRIORITY 7: Monetization Infrastructure

### 7.1 Legal Pages (Required)
**Status:** TODO  
**Timeline:** Week 1-2  
**Impact:** AdSense/Affiliate compliance

```markdown
Tasks:
- [ ] Create /privacy-policy page
- [ ] Create /terms-of-service page
- [ ] Create /affiliate-disclosure page
- [ ] Add cookie consent banner (GDPR)
- [ ] Add footer links to all legal pages
- [ ] Include affiliate disclaimer on articles
```

### 7.2 Affiliate Program Setup
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Revenue foundation

```markdown
Tasks:
- [ ] Apply for Amazon Associates (lawncare0c-20)
- [ ] Apply for ShareASale (lawn brands)
- [ ] Research Home Depot affiliate program
- [ ] Save affiliate IDs in secure config
- [ ] Test affiliate links work
- [ ] Set up conversion tracking
```

### 7.3 Display Advertising
**Status:** TODO  
**Timeline:** Week 4 (need 15+ articles)  
**Impact:** Passive revenue

```markdown
Tasks:
- [ ] Publish 15+ quality articles first
- [ ] Apply for Google AdSense
- [ ] Create ad placement strategy (non-intrusive)
- [ ] Implement ad components in Next.js
- [ ] Test page speed with ads
- [ ] Monitor RPM and optimize
```

### 7.4 Email List Building
**Status:** TODO  
**Timeline:** Month 2  
**Impact:** Owned audience, long-term revenue

```markdown
Tasks:
- [ ] Sign up for ConvertKit/Mailchimp free tier
- [ ] Create lead magnet: "Seasonal Lawn Care Calendar PDF"
- [ ] Build email signup form component
- [ ] Add to article sidebar/footer
- [ ] Create welcome email sequence
- [ ] Plan weekly newsletter content
```

---

## 📋 PRIORITY 8: Analytics & Performance

### 8.1 Google Analytics 4
**Status:** TODO  
**Timeline:** Week 1  
**Impact:** Data-driven decisions

```markdown
Tasks:
- [ ] Create GA4 property
- [ ] Add tracking code to Next.js
- [ ] Set up conversion events:
  - [ ] Email signup
  - [ ] Affiliate link click
  - [ ] Article completion (scroll depth)
  - [ ] Time on page
- [ ] Create custom dashboard
- [ ] Set up weekly email reports
```

### 8.2 Technical SEO
**Status:** TODO  
**Timeline:** Week 2  
**Impact:** Search rankings

```markdown
Tasks:
- [ ] Generate XML sitemap automatically
- [ ] Create robots.txt
- [ ] Add canonical URLs
- [ ] Implement JSON-LD structured data
- [ ] Add Open Graph meta tags
- [ ] Optimize Core Web Vitals
- [ ] Target 90+ PageSpeed score
```

### 8.3 Performance Monitoring
**Status:** TODO  
**Timeline:** Ongoing  

```markdown
Tasks:
- [ ] Set up uptime monitoring (UptimeRobot free)
- [ ] Monitor build times
- [ ] Track image optimization effectiveness
- [ ] Weekly PageSpeed audits
- [ ] Monitor Vercel analytics
```

---

## 📋 PRIORITY 9: Content Automation

### 9.1 Scheduled Content Generation
**Status:** TODO  
**Timeline:** Month 2  
**Impact:** Hands-off content production

```yaml
# .github/workflows/generate-content.yml
name: Daily Content Generation

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate articles
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python content_generator.py --count 3
      
      - name: Commit to drafts branch
        run: |
          git checkout -b drafts-$(date +%Y%m%d)
          git add drafts/
          git commit -m "Auto-generated content $(date)"
          git push origin HEAD
```

### 9.2 Approval Workflow
**Status:** TODO  
**Timeline:** Month 2  
**Impact:** Quality control with minimal effort

```markdown
Tasks:
- [ ] Build simple admin dashboard
- [ ] List pending drafts with preview
- [ ] One-click approve/reject
- [ ] Auto-move approved to published
- [ ] Trigger Vercel rebuild
- [ ] Email notification of new drafts
```

---

## 🚀 EXECUTION TIMELINE

### Week 1: Foundation
- [ ] Day 1: Git init, GitHub repo, .gitignore
- [ ] Day 2: Deploy to Vercel, connect domain
- [ ] Day 3: Verify GSC, submit sitemap
- [ ] Day 4: Update image prompts for photorealism
- [ ] Day 5: Implement mid-article section images
- [ ] Day 6: Image SEO (alt, title, caption)
- [ ] Day 7: Shorten articles to 800-1000 words

### Week 2: Quality & Revenue Systems
- [ ] Day 8: Create curated keyword database (100+ keywords)
- [ ] Day 9: Implement keyword selector
- [ ] Day 10: **Build article QA evaluation system**
- [ ] Day 11: **Implement auto-refinement loop**
- [ ] Day 12: **Create feedback logger & pattern analyzer**
- [ ] Day 13: Build affiliate link automation
- [ ] Day 14: Create legal pages (privacy, disclosure)

### Week 3: Search, Analytics & Scale
- [ ] Day 15: Apply for Amazon Associates
- [ ] Day 16: Set up Google Analytics 4
- [ ] Day 17: Implement Algolia search (if 20+ articles)
- [ ] Day 18: Technical SEO (sitemap, schema)
- [ ] Day 19: Generate 10 articles with full pipeline (QA enabled)
- [ ] Day 20: **Run first weekly QA insights analysis**
- [ ] Day 21: Review insights, apply prompt improvements

### Week 4: Optimization & Content Push
- [ ] Day 22: Google Trends integration
- [ ] Day 23: People Also Ask scraper
- [ ] Day 24: Generate 15 more articles
- [ ] Day 25: Review and publish batch
- [ ] Day 26: Performance optimization
- [ ] Day 27: **Second weekly QA analysis - refine prompts**
- [ ] Day 28: Monitor metrics and iterate

### Month 2: Scale & Automate
- [ ] Apply for Google AdSense
- [ ] Set up email list
- [ ] Implement GitHub Actions automation
- [ ] Build approval dashboard
- [ ] **Monthly QA trend analysis**
- [ ] Generate 50+ more articles
- [ ] Integrate GSC data (if available)

---

## ❓ OUTSTANDING QUESTIONS FOR USER

1. **Writing Samples:** Please provide 3-5 paragraphs in your desired voice/tone

2. **Amazon Affiliate Tag:** Do you have your Associates ID yet, or need to apply?

3. **Daily Article Volume:** How many articles per day is sustainable for review? (Recommend 3-5)

4. **Hostinger DNS Access:** Do you need help configuring domain DNS?

5. **Priority Check:** Is photorealistic images or keyword system more urgent?

---

## 📊 SUCCESS METRICS

### Week 1
- [ ] Site live at lawncare.center
- [ ] 5+ articles with dual images published
- [ ] GSC verified and sitemap submitted

### Month 1
- [ ] 30+ articles published
- [ ] Search functionality working
- [ ] Affiliate links in all articles
- [ ] Google indexing pages

### Month 3
- [ ] 100+ articles published
- [ ] 5,000+ monthly visitors
- [ ] $50-100/month revenue
- [ ] First page rankings for 5+ keywords

### Month 6
- [ ] 200+ articles published
- [ ] 15,000+ monthly visitors
- [ ] $200-400/month revenue
- [ ] Email list: 500+ subscribers

### Month 12
- [ ] 400+ articles published
- [ ] 40,000+ monthly visitors
- [ ] $800-1,200/month revenue
- [ ] Fully automated pipeline
- [ ] Authority site status achieved

---

## 💰 COST PROJECTIONS

### Per Article Cost Breakdown
| Component | Cost | Notes |
|-----------|------|-------|
| Claude text generation | $0.03-0.05 | Base article (800-1000 words) |
| DALL-E 3 hero image | $0.08 | 1792x1024 landscape |
| DALL-E 3 section image | $0.04 | 1024x1024 square |
| **QA Evaluation** | $0.02-0.03 | Quality scoring |
| **Refinement (40% of articles)** | $0.01-0.02 | Averaged across all |
| Affiliate link detection | $0.01 | Product scanning |
| **Total per article** | **$0.19-0.23** | Full pipeline |

### Monthly Operating Costs (100 Articles)
| Item | Cost | Notes |
|------|------|-------|
| Claude API (text + QA) | $7-10 | Generation + evaluation + refinement |
| DALL-E 3 (images) | $12-16 | 2 images per article |
| Affiliate detection | $1 | Product scanning |
| Vercel Hosting | $0 | Free tier |
| Algolia Search | $0 | Free tier (10K searches) |
| Domain | $0 | Already owned |
| **Total** | **$20-27/month** | For 100 quality articles |

### Cost Comparison
| Scenario | Per Article | 100 Articles/Month |
|----------|-------------|-------------------|
| Text only (no images) | $0.03-0.05 | $3-5 |
| Text + 1 image | $0.11-0.13 | $11-13 |
| Text + 2 images | $0.15-0.17 | $15-17 |
| **Full pipeline (text + 2 images + QA + affiliates)** | **$0.19-0.23** | **$20-27** |

### What You Get for the Extra Cost
- **QA System ($5-8/month):** 40% fewer manual edits, self-improving quality
- **Second Image ($4/month):** Better engagement, lower bounce rate
- **Affiliate Detection ($1/month):** Automated monetization

### Revenue Projections (Conservative)
| Month | Traffic | Ad Revenue | Affiliate | Total | Net Profit |
|-------|---------|------------|-----------|-------|------------|
| 3 | 2,000 | $16 | $30 | $46 | $19-26 |
| 6 | 10,000 | $80 | $150 | $230 | $203-210 |
| 12 | 40,000 | $320 | $600 | $920 | $893-900 |

**Break-even:** Month 2-3 (costs $20-27, revenue starts Month 2)
**ROI at Month 12:** ~3,400% ($900 revenue / $27 cost)

---

*This TODO list is optimized for Claude Code execution. Update status as tasks complete.*

**Version:** 2.0  
**Last Updated:** November 15, 2025  
**Next Review:** Weekly
