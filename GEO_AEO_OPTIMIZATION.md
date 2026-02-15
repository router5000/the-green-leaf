# Claude Code Task List: GEO/AEO Optimization for thegreenleaf.com

**Goal:** Maximize visibility in AI-generated answers (ChatGPT, Perplexity, Google AI Overviews) and traditional Google search results.

**Project:** thegreenleaf.com
**GitHub:** https://github.com/JakeTaylorDesign/cannabiscare-center

---

## STATUS REVIEW (January 2026)

### Completed
| Task | Status | Implementation |
|------|--------|----------------|
| 1. FAQ Schema | DONE | FAQPage schema from `post.faqs` in page.tsx |
| 2. HowTo Schema | DONE | Auto-detected from H2 "Step-by-Step"/"How to" sections with H3 sub-steps |
| 3. Speakable Schema | DONE | Points to `.quick-answer`, `[itemprop="description"]`, `[itemprop="headline"]` |
| 4. llms.txt | DONE | Full rewrite to llmstxt.org standard |
| 5. Quick Answer wrapper | DONE | `<section class="quick-answer">` wraps Quick Answer content |
| 6. TL;DR / Bottom Line | DONE | `TLDRSummary` component + `tldr` field |
| 7. Table of Contents | DONE | Auto-generated from H2/H3 headings with jump links |
| 8. About/Author page | DONE | `/about` with Organization + WebSite schema, E-E-A-T signals |
| 9. Last Updated | DONE | `dateModified` uses `post.last_updated || post.generated_at` |
| 10. Citation schema | DONE | Sources parsed, `citation` array in Article schema, HTML markup |
| 11. FAQ / People Also Ask | DONE | `FAQSection` accordion + 3-5 FAQs per article |
| 13. Key Stats box | DONE | `KeyStatCallout` component + `key_stat` field |
| 14. Breadcrumbs | DONE | Visual + BreadcrumbList schema (missing category level until taxonomy added) |
| 15. Topic hub pages | DONE | CollectionPage + ItemList schema on /topics |
| 17. Seasonal badges | DONE | Season badge in article header |

| 16. Category taxonomy | DONE | 66 articles backfilled, breadcrumbs + schema use category |
| 19. Freshness automation | DONE | `freshness_tracker.py` with staleness/seasonal/citation checks |
| 21. AI crawler access | DONE | `robots.txt` explicitly allows GPTBot/ClaudeBot/PerplexityBot/CCBot |

| 12. Comparison tables | DONE | Prompt includes table for "vs" keywords; posts.ts adds semantic attrs |
| 20. Validate structured data | DONE | All 66 articles pass schema field validation |

### Remaining
| Task | Status | Notes |
|------|--------|-------|
| 18. Printable checklists | DONE | PrintableChecklist component with print button, shows on 34 HowTo articles |

---

## HIGH PRIORITY - Structured Data & Schema

### 1. Add FAQ Schema to Articles
- **Location:** `site/src/app/articles/[slug]/page.tsx`
- **Task:** Extract Q&A patterns from article content and generate FAQPage schema
- **Why:** FAQ schema is heavily used by AI answer engines and Google featured snippets
- **Implementation:** Parse H2/H3 questions from content, pair with following paragraph as answer

### 2. Add HowTo Schema for Step-by-Step Articles
- **Location:** `site/src/app/articles/[slug]/page.tsx`
- **Task:** Detect articles with step-by-step instructions and generate HowTo schema with steps, tools, supplies
- **Why:** HowTo schema appears in rich results and AI summaries
- **Detection:** Look for "Step 1", "How to", numbered lists in content

### 3. Implement Speakable Schema
- **Location:** `site/src/app/articles/[slug]/page.tsx`
- **Task:** Add Speakable schema pointing to "Quick Answer" and "Key Takeaways" sections
- **Why:** Voice assistants and AI readers prioritize speakable content

### 4. Enhance llms.txt File
- **Location:** `site/public/llms.txt`
- **Task:** Create comprehensive llms.txt following the emerging standard (https://llmstxt.org/)
- **Include:** Site purpose, content categories, key topics, API access info, citation preferences
- **Why:** Helps LLMs understand and properly cite your content

---

## HIGH PRIORITY - Content Structure for AI

### 5. Add "Quick Answer" JSON-LD Snippet
- **Location:** `content_generator.py`
- **Task:** Ensure every article's Quick Answer section is:
  - Wrapped in semantic `<section class="quick-answer">`
  - Maximum 2-3 sentences (under 50 words)
  - Directly answers the title question
  - Marked with `itemprop="description"` for schema

### 6. Create Definitive Answer Blocks
- **Location:** `content_generator.py`
- **Task:** Add a "The Bottom Line" or "Definitive Answer" section at article end
- **Format:** Single paragraph summary optimized for AI extraction
- **Why:** AI engines often pull from conclusion sections

### 7. Add Table of Contents with Jump Links
- **Location:** `site/src/components/ArticleContent.tsx`
- **Task:** Auto-generate TOC from H2/H3 headings with anchor links
- **Why:** Improves content navigation signals for both users and AI crawlers

---

## MEDIUM PRIORITY - E-E-A-T Signals

### 8. Create Author/Expert Page
- **Location:** `site/src/app/about/page.tsx` (new)
- **Task:** Create About page with:
  - Site mission and expertise claims
  - Content methodology (AI-assisted with expert review)
  - Source verification process
  - Contact information
- Add Person schema for author entity

### 9. Add "Last Updated" Display and Schema
- **Location:** `site/src/app/articles/[slug]/page.tsx`
- **Task:** Display "Last Updated: [date]" prominently
- Add `dateModified` to Article schema
- **Why:** Freshness signals matter for AI answer selection

### 10. Enhance Source Citations
- **Location:** `content_generator.py`
- **Task:** Add `citation` schema markup to Sources section
- Ensure sources link to specific pages, not just domains
- **Why:** AI engines trust content with verifiable citations

---

## MEDIUM PRIORITY - Content Optimization

### 11. Add "People Also Ask" Section
- **Location:** `content_generator.py`
- **Task:** Generate 3-5 related questions with concise answers at article end
- **Format:** Accordion-style Q&A
- Add FAQ schema for this section
- **Why:** Directly targets PAA boxes and AI follow-up queries

### 12. Create Comparison/Vs Tables
- **Location:** `content_generator.py`
- **Task:** For relevant topics, add comparison tables (e.g., "Liquid vs Granular Fertilizer")
- Use semantic `<table>` with `<thead>` and `<caption>`
- **Why:** Tables are frequently extracted by AI for quick comparisons

### 13. Add "Key Stats" or "Quick Facts" Box
- **Location:** `content_generator.py`
- **Task:** Include a highlighted box with 3-5 key statistics/facts
- Use microdata attributes
- **Why:** AI engines love extractable factual nuggets

---

## MEDIUM PRIORITY - Technical SEO

### 14. Implement Breadcrumb Navigation
- **Location:** `site/src/app/articles/[slug]/page.tsx`
- **Task:** Add visual breadcrumbs (Home > Articles > [Category] > [Title])
- Ensure BreadcrumbList schema is complete with all levels
- **Why:** Helps AI understand site hierarchy and content relationships

### 15. Create Topic Cluster Hub Pages
- **Location:** `site/src/app/topics/[topic]/page.tsx`
- **Task:** Enhance topic pages to be comprehensive hub pages
- **Include:** Overview, linked articles, FAQ, related topics
- Add CollectionPage or ItemList schema
- **Why:** Establishes topical authority for AI evaluation

### 16. Add Article Category Taxonomy
- **Location:** Frontmatter in `content_generator.py`
- **Task:** Add consistent category field (Cannabis Basics, Seasonal Care, Problem Solving, Equipment, etc.)
- Use categories in internal linking and topic pages
- **Why:** Helps AI understand content relationships

---

## LOWER PRIORITY - Enhanced Features

### 17. Add Seasonal Content Badges
- **Location:** `site/src/components/ArticleContent.tsx`
- **Task:** Display "Best for: Spring/Summer/Fall/Winter" badges
- Include in Article schema as `about` or custom property
- **Why:** Helps AI serve seasonally appropriate answers

### 18. Create Printable Checklists
- **Location:** `content_generator.py` + new component
- **Task:** For how-to articles, generate downloadable/printable checklist
- **Why:** Increases page value and engagement signals

---

## INFRASTRUCTURE

### 19. Add Content Freshness Automation
- **Location:** `freshness_tracker.py` + GitHub Actions
- **Task:** Auto-flag articles older than 6 months for review
- Update `dateModified` when content refreshed
- **Why:** AI engines prefer fresh content

---

## VALIDATION TASKS

### 20. Test Structured Data
- **Task:** Run all pages through Google Rich Results Test
- Fix any schema validation errors
- Test with Schema.org validator

### 21. Test AI Crawler Access
- **Task:** Verify GPTBot, ClaudeBot, PerplexityBot can access content
- Check server logs for AI crawler activity
- Test fetch as different user agents

---

## Revised Implementation Schedule

| Week | Tasks | Focus Area |
|------|-------|------------|
| **Week 1** | 9 fix, 4, 2, 3, 5 | Schema fixes + llms.txt + HowTo/Speakable |
| **Week 2** | 7, 8, 10 | TOC + About page + Citations |
| **Week 3** | 15, 16, 12 | Topic hubs + Taxonomy + Content enhancements |
| **Week 4** | 19, 20, 21 | Automation + Validation |
| **Already Done** | 1, 6, 11, 13, 14, 17 | FAQ schema, TL;DR, Key Stats, Breadcrumbs, Season badges |

---

## Quick Reference: File Locations

| File | Purpose |
|------|---------|
| `site/src/app/articles/[slug]/page.tsx` | Article detail page (schema, display) |
| `site/src/components/ArticleContent.tsx` | Article rendering component |
| `content_generator.py` | Article generation (content structure) |
| `site/public/llms.txt` | LLM access and citation guidance |
| `site/public/robots.txt` | Crawler permissions |
| `freshness_tracker.py` | Content freshness monitoring |

---

## Success Metrics

- [ ] All articles have FAQ or HowTo schema (validate with Rich Results Test)
- [ ] llms.txt properly configured and accessible
- [ ] Quick Answer sections under 50 words on all articles
- [ ] About/Author page live with Person schema
- [ ] dateModified displaying and in schema for all articles
- [ ] Topic hub pages created for top 5 categories
- [ ] AI crawler access verified in server logs
