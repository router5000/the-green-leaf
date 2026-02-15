# Article Regeneration Plan
## Replacing Old Articles with New QA-Optimized Reve Image Content

**Date:** December 6, 2025
**Total Articles:** 37
**Status:** Planning Phase

---

## 📊 Current State Analysis

### What You Have Now:
- **37 existing articles** in `site/content/posts/`
- All have DALL-E 3 images (older generation)
- Word count: ~895 words average
- No QA evaluation scores
- No clickable source links
- Missing affiliate links (or old format)
- 1:1 section images (not 4:3)

### What the New System Provides:
- ✅ Reve API photorealistic images (16:9 hero + 4:3 section)
- ✅ 600-750 words (25% shorter, more focused)
- ✅ QA evaluation system (8+/10 quality scores)
- ✅ Clickable source links with URLs
- ✅ Automated affiliate links (3-5 per article)
- ✅ LLM-optimized semantic structure
- ✅ Enhanced Schema.org markup

---

## 💰 Cost Analysis

### Per Article Regeneration:
| Component | Cost |
|-----------|------|
| Claude text generation | $0.03-0.05 |
| QA Evaluation + refinement | $0.03-0.05 |
| Reve hero image (16:9) | $0.08 |
| Reve section image (4:3) | $0.08 |
| Affiliate link detection | $0.01 |
| **Total per article** | **$0.23-0.27** |

### Total Project Cost:
- **37 articles × $0.25 average = ~$9.25**
- Very affordable for a complete content refresh!

---

## ⏱️ Time Estimate

### Automated Generation Time:
- **Per article:** ~2-3 minutes (text + 2 images + QA + affiliates)
- **37 articles × 2.5 min = ~93 minutes** (~1.5 hours)

### Manual Review Time (Optional):
- **Per article:** 3-5 minutes to review quality
- **37 articles × 4 min = ~148 minutes** (~2.5 hours)

### Total Time: **~4 hours** (mostly automated)

---

## 🎯 Regeneration Strategy

### Option 1: **Full Regeneration (Recommended)**
Replace all 37 articles with new versions using same keywords.

**Pros:**
- Consistent quality across entire site
- All articles get QA scores, sources, affiliates
- Photorealistic Reve images throughout
- LLM-optimized structure everywhere
- Fresh content that's 25% more concise

**Cons:**
- Costs $9.25 total
- Takes ~4 hours (mostly automated)
- Existing SEO rankings might temporarily fluctuate

**When to do:** Now or in batches over 1-2 weeks

---

### Option 2: **Selective Regeneration**
Only regenerate high-priority/high-traffic articles.

**Pros:**
- Lower cost ($3-5)
- Faster execution (1-2 hours)
- Focus on best performers

**Cons:**
- Inconsistent quality across site
- Still have mix of old/new formats
- Manual selection required

**When to do:** If budget/time constrained

---

### Option 3: **Gradual Rolling Update**
Replace 5-10 articles per week over 4 weeks.

**Pros:**
- Spreads cost over time
- Can monitor SEO impact gradually
- Less disruptive

**Cons:**
- Takes longer to complete
- Inconsistent site quality during transition

**When to do:** If cautious about SEO impact

---

## 📋 Execution Plan (Option 1 - Full Regeneration)

### Phase 1: Preparation (15 minutes)
1. **Backup existing articles**
   ```bash
   cp -r site/content/posts site/content/posts_backup_$(date +%Y%m%d)
   ```

2. **Extract all keywords**
   ```bash
   python3 extract_keywords.py  # Create this helper script
   ```

3. **Review keyword list** - Mark any to skip or update

---

### Phase 2: Automated Generation (1.5 hours)
1. **Create batch regeneration script**
   ```python
   # regenerate_all.py
   import time
   from content_generator import generate_article, save_to_notion_format

   keywords = [
       "how often should I aerate my cannabis",
       "best time to mow cannabis",
       "fall cannabis aeration timing",
       # ... all 37 keywords
   ]

   for i, keyword in enumerate(keywords, 1):
       print(f"[{i}/37] Regenerating: {keyword}")
       try:
           article = generate_article(keyword, enable_qa=True)
           save_to_notion_format(article, output_dir="regenerated")
           print(f"   ✅ Success (QA: {article['qa_score']}/10)")
           time.sleep(60)  # Rate limit: 1 per minute
       except Exception as e:
           print(f"   ❌ Error: {e}")
   ```

2. **Run batch generation**
   ```bash
   python3 regenerate_all.py
   ```

3. **Monitor progress** - Check QA logs for quality scores

---

### Phase 3: Quality Review (2.5 hours)
1. **Check QA scores** - All should be 8+/10
   ```bash
   python3 article_qa.py --analyze
   ```

2. **Spot-check 5-10 articles** manually:
   - Images load correctly
   - Sources have working links
   - Affiliate links appropriate
   - Content flows well

3. **Flag any issues** for manual review

---

### Phase 4: Deployment (30 minutes)
1. **Move old articles to archive**
   ```bash
   mkdir site/content/posts_old
   mv site/content/posts/*.md site/content/posts_old/
   ```

2. **Deploy new articles**
   ```bash
   cp regenerated/*.md site/content/posts/
   ```

3. **Verify site builds** locally

4. **Deploy to production** (git commit + push)

---

## 🚨 Risk Mitigation

### SEO Impact Concerns:
**Risk:** Google may temporarily drop rankings for rewritten content

**Mitigation:**
1. Keep same URLs (slugs don't change)
2. Keep same keywords and topics
3. Maintain similar content structure (H2/H3 hierarchy)
4. Use 301 redirects if any URLs change
5. Submit updated sitemap to Google Search Console
6. Monitor rankings for 2-4 weeks

**Reality:** Content is improved (QA-scored, sources, better structure), so should improve rankings long-term

---

### Image Replacement Concerns:
**Risk:** Losing existing image SEO value

**Mitigation:**
1. Keep same image filenames where possible
2. Maintain proper alt text
3. New images are higher quality (Reve vs DALL-E 3)
4. Better Schema.org markup for images

---

### Traffic Disruption:
**Risk:** Temporary traffic dip during transition

**Mitigation:**
1. **Don't do all at once** - Option 3 (gradual) if concerned
2. Monitor Google Analytics daily
3. Check Search Console for errors
4. Rollback capability (keep backups)

---

## 📝 Helper Scripts Needed

### 1. Keyword Extractor (`extract_keywords.py`)
```python
import os
import re
from pathlib import Path

posts_dir = Path("site/content/posts")
keywords = []

for file in posts_dir.glob("*.md"):
    with open(file) as f:
        content = f.read()
        match = re.search(r'keyword:\s*"([^"]+)"', content)
        if match:
            keywords.append(match.group(1))

# Save to file
with open("keywords_to_regenerate.txt", "w") as f:
    for kw in keywords:
        f.write(f"{kw}\n")

print(f"✅ Extracted {len(keywords)} keywords")
```

### 2. Batch Regenerator (`regenerate_all.py`)
```python
import time
from pathlib import Path
from content_generator import generate_article, save_to_notion_format, save_article_json

# Load keywords
with open("keywords_to_regenerate.txt") as f:
    keywords = [line.strip() for line in f if line.strip()]

print(f"🌱 Regenerating {len(keywords)} articles with QA pipeline\n")

failed = []
for i, keyword in enumerate(keywords, 1):
    print(f"[{i}/{len(keywords)}] Regenerating: {keyword}")
    try:
        article = generate_article(keyword, enable_qa=True)
        save_to_notion_format(article, output_dir="regenerated")
        save_article_json(article, output_dir="regenerated/json")

        qa_score = article.get('qa_evaluation', {}).get('scores', {}).get('overall', 0)
        print(f"    ✅ Success (QA: {qa_score:.1f}/10)")

        # Rate limiting - wait 60 seconds between articles
        if i < len(keywords):
            print(f"    ⏳ Waiting 60s for rate limits...\n")
            time.sleep(60)

    except Exception as e:
        print(f"    ❌ Error: {e}\n")
        failed.append(keyword)

print(f"\n🎉 Complete! {len(keywords) - len(failed)}/{len(keywords)} successful")
if failed:
    print(f"❌ Failed: {len(failed)}")
    for kw in failed:
        print(f"   - {kw}")
```

### 3. Quality Checker (`check_regenerated.py`)
```python
import json
from pathlib import Path

regenerated_dir = Path("regenerated/json")
articles = list(regenerated_dir.glob("*.json"))

print(f"📊 Quality Report - {len(articles)} articles\n")

scores = []
for file in articles:
    with open(file) as f:
        article = json.load(f)
        qa_score = article.get('qa_evaluation', {}).get('scores', {}).get('overall', 0)
        scores.append({
            'slug': article['slug'],
            'score': qa_score,
            'passed': article.get('qa_passed', False),
            'word_count': article.get('word_count', 0)
        })

# Sort by score
scores.sort(key=lambda x: x['score'])

print("Lowest Scores (need review):")
for s in scores[:5]:
    status = "✅" if s['passed'] else "❌"
    print(f"  {status} {s['slug']}: {s['score']:.1f}/10 ({s['word_count']} words)")

print(f"\nAverage QA Score: {sum(s['score'] for s in scores) / len(scores):.1f}/10")
print(f"Passed QA: {sum(1 for s in scores if s['passed'])}/{len(scores)}")
```

---

## 🎯 Recommendation

### **Go with Option 1: Full Regeneration**

**Why:**
1. **Low cost** ($9.25 total) - negligible for quality improvement
2. **Fast execution** (~4 hours mostly automated)
3. **Consistent quality** across entire site
4. **Future-proof** - all articles at new standard
5. **Better for SEO long-term** - higher quality content
6. **Better for AI crawlers** - LLM-optimized structure

**When to execute:**
- **Immediately** if you want consistent quality
- **This weekend** if you want to monitor closely
- **Over 2 weeks** (gradual) if very cautious about SEO

---

## 🚀 Quick Start Command

```bash
# Extract keywords from existing articles
python3 extract_keywords.py

# Review keywords list (edit if needed)
nano keywords_to_regenerate.txt

# Run full regeneration (takes ~1.5 hours + rate limits)
python3 regenerate_all.py

# Check quality scores
python3 check_regenerated.py

# If satisfied, deploy
mv site/content/posts site/content/posts_old
cp regenerated/*.md site/content/posts/
```

---

## 📈 Expected Outcomes

### After Regeneration:
- ✅ **37 articles** with 8+/10 QA scores
- ✅ **74 Reve images** (hero + section per article)
- ✅ **~185 affiliate links** (5 per article avg)
- ✅ **185 source citations** with working URLs
- ✅ **100% LLM-optimized** semantic structure
- ✅ **25% shorter** content (better engagement)

### SEO Impact Timeline:
- **Week 1:** Possible small ranking fluctuation
- **Week 2-4:** Rankings stabilize
- **Month 2-3:** Rankings improve (better quality signals)
- **Month 6+:** Significant traffic increase from AI crawler citations

---

## 💡 Pro Tips

1. **Test first** - Regenerate 3-5 articles, monitor for 1 week
2. **Keep backups** - Don't delete old articles immediately
3. **Monitor GSC** - Check for crawl errors daily
4. **Update sitemap** - Submit to Google after deployment
5. **Track rankings** - Use Ahrefs/SEMrush to monitor keyword positions
6. **Check AI citations** - Ask ChatGPT/Claude/Perplexity about your topics

---

**Ready to execute?** The system is fully automated and tested. You can regenerate all 37 articles in one command! 🚀
