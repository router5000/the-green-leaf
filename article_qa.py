#!/usr/bin/env python3
"""
Article Quality Assurance System
Multi-dimensional evaluation, auto-refinement, and feedback logging
Ensures articles are optimized for both search engines and LLM crawlers
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from rate_limiter import wait_for_claude
from cost_tracker import get_tracker

load_dotenv()
# Explicit per-request timeout — a slow/hung evaluate or refine call should
# fail fast instead of silently eating the caller's overall time budget.
CLAUDE_CALL_TIMEOUT = 90.0
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"), max_retries=2)

# Quality thresholds
QUALITY_THRESHOLDS = {
    'accuracy': 7.0,
    'seo_score': 7.0,
    'impact_score': 7.0,
    'structure_score': 7.0,
    'sources_score': 6.5,
    'overall': 8.0  # auto-publish threshold: score >= this publishes, no human gate ever
}

MAX_REFINEMENT_ROUNDS = 2


def evaluate_article(content: str, keyword: str, title: str, meta_description: str) -> dict:
    """
    Comprehensive article evaluation using Claude.

    Scores on multiple dimensions:
    - Accuracy (factual correctness, completeness)
    - SEO (keyword usage, structure, meta optimization)
    - Impact (actionability, readability, engagement)
    - Structure (LLM-friendly formatting, semantic HTML readiness)
    - Sources (credible citations, authoritative references)

    Returns: Detailed evaluation with scores and specific issues
    """

    evaluation_prompt = f"""You are a professional content quality evaluator specializing in cannabis content, SEO, and AI-readability optimization.

Evaluate this article on multiple dimensions and provide actionable feedback.

**Article Details:**
Title: {title}
Target Keyword: {keyword}
Meta Description: {meta_description}

**Article Content:**
{content}

**Evaluation Criteria:**

1. **ACCURACY (1-10)**: Factual correctness, completeness, expert-level advice
   - Are cannabis recommendations factually correct?
   - Are measurements, timing, and frequencies accurate?
   - Is advice safe and effective?
   - Are there any misleading or dangerous suggestions?

2. **SEO OPTIMIZATION (1-10)**: Search engine optimization
   - Is the target keyword in the first 100 words?
   - Is keyword density appropriate (1-2%)?
   - Are H2/H3 headings optimized with related keywords?
   - Is the meta description compelling and within 150-160 chars?
   - Does it have a "Quick Answer" section at the top?
   - Are there 3-5 "Key Takeaways" bullet points?

3. **IMPACT & ENGAGEMENT (1-10)**: Actionability, readability, usefulness
   - Is the advice actionable and practical?
   - Are instructions clear and step-by-step?
   - Is it written at an 8th-grade reading level?
   - Does it avoid jargon and technical overload?
   - Are there specific numbers, measurements, and timing?

4. **STRUCTURE & LLM-FRIENDLINESS (1-10)**: AI crawler optimization
   - Clear hierarchical heading structure (H1 → H2 → H3)?
   - Proper markdown list syntax (using `-` not `•`)?
   - Well-structured paragraphs (2-4 sentences each)?
   - Logical content flow and organization?
   - Semantic clarity for AI understanding?

5. **SOURCES & CREDIBILITY (1-10)**: Citations and references
   - Are there 4-6 diverse, credible sources cited?
   - Are CLICKABLE numbered citations [[1]](#user-content-fn-1), [[2]](#user-content-fn-2) used throughout text (8-12 minimum)?
   - Do citations link to anchor IDs in the Sources section (<a id="user-content-fn-1"></a>)?
   - Are sources varied (different university extensions, industry sources, research publications)?
   - Is there a "## Sources" section at the bottom with anchor IDs for each source?
   - Are all sources CLICKABLE LINKS in markdown format: "1. [Name](URL) - Description"?
   - Are URLs realistic main domains (not deep links that might 404)?
   - Do sources include mix of: university extensions, industry/manufacturer research, and other credible publications?
   - Are the specific sources appropriate and relevant to this article's topic?

**Output Format (JSON only):**
{{
    "scores": {{
        "accuracy": 8.5,
        "seo_score": 7.0,
        "impact_score": 9.0,
        "structure_score": 8.0,
        "sources_score": 6.0,
        "overall": 7.7
    }},
    "issues": [
        {{
            "category": "seo",
            "severity": "high",
            "issue": "Keyword not in first paragraph",
            "fix": "Add keyword to opening sentence"
        }},
        {{
            "category": "sources",
            "severity": "critical",
            "issue": "No sources cited",
            "fix": "Add 3-5 authoritative sources at bottom"
        }}
    ],
    "strengths": [
        "Clear step-by-step instructions",
        "Good use of specific measurements"
    ],
    "requires_refinement": true,
    "priority_fixes": [
        "Add clickable citations [[1]](#user-content-fn-1)[[2]](#user-content-fn-2) throughout text (8-12 minimum)",
        "Add Sources section with anchor IDs (<a id=\"user-content-fn-1\"></a>) for each source",
        "Add 4-6 diverse sources (university extensions + industry + research)",
        "Include keyword in first 100 words",
        "Ensure citation links match anchor IDs in Sources section"
    ]
}}

Return ONLY valid JSON, no other text."""

    # Rate limit Claude API calls
    wait_for_claude()

    step_start = time.time()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        timeout=CLAUDE_CALL_TIMEOUT,
        messages=[{"role": "user", "content": evaluation_prompt}]
    )
    print(f"      ⏱️  QA evaluate call took {time.time() - step_start:.1f}s")

    # Log Claude API usage for cost tracking
    tracker = get_tracker()
    if tracker:
        tracker.log_claude_usage(message.usage, "claude-sonnet-4-6")

    response_text = message.content[0].text

    # Parse JSON response
    try:
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            evaluation = json.loads(json_str)
        elif "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            evaluation = json.loads(response_text[start:end])
        else:
            evaluation = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"   ⚠️  Evaluation parsing error: {e}")
        print(f"   Response: {response_text[:500]}")
        # Return a default evaluation
        evaluation = {
            "scores": {"accuracy": 7.0, "seo_score": 7.0, "impact_score": 7.0,
                      "structure_score": 7.0, "sources_score": 5.0, "overall": 6.6},
            "issues": [{"category": "system", "severity": "high",
                       "issue": "Evaluation parsing failed", "fix": "Manual review needed"}],
            "strengths": [],
            "requires_refinement": True,
            "priority_fixes": ["Manual quality review required"]
        }

    return evaluation


def refine_article(content: str, keyword: str, title: str, meta_description: str, evaluation: dict) -> dict:
    """
    Automatically refine article based on evaluation feedback.

    Applies targeted fixes:
    - Add missing Quick Answer section
    - Improve keyword placement
    - Add source citations
    - Fix structure issues
    - Enhance actionability

    Returns: Refined article data with updated content
    """

    issues_text = "\n".join([
        f"- [{issue['severity'].upper()}] {issue['category']}: {issue['issue']} → {issue['fix']}"
        for issue in evaluation['issues']
    ])

    priority_fixes_text = "\n".join([f"- {fix}" for fix in evaluation['priority_fixes']])

    refinement_prompt = f"""You are refining a cannabis article based on quality evaluation feedback.

**Original Article:**
Title: {title}
Target Keyword: {keyword}
Meta Description: {meta_description}

{content}

**Evaluation Scores:**
- Accuracy: {evaluation['scores']['accuracy']}/10
- SEO: {evaluation['scores']['seo_score']}/10
- Impact: {evaluation['scores']['impact_score']}/10
- Structure: {evaluation['scores']['structure_score']}/10
- Sources: {evaluation['scores']['sources_score']}/10

**Issues Found:**
{issues_text}

**Priority Fixes Required:**
{priority_fixes_text}

**Your Task:**
Rewrite the article to address ALL issues above while maintaining the original voice and style.

**CRITICAL REQUIREMENTS:**

1. **Clickable Citations Throughout Text**:
   - Add CLICKABLE numbered citations that link to Sources section
   - Format: "This is a fact[[1]](#user-content-fn-1)."
   - Multiple citations: "Combined facts[[1]](#user-content-fn-1)[[2]](#user-content-fn-2)."
   - Place citations at END of sentences, before the period
   - Use 8-12 citations distributed naturally across sections

2. **Diverse Sources Section with Anchor IDs**: Add "## Sources" at bottom with 4-6 DIVERSE credible references:
   - At least 2 DIFFERENT university extensions (vary by topic - use extensions relevant to THIS specific topic)
   - At least 1 industry/manufacturer source (Pennington, Scotts, Milorganite, etc.)
   - At least 1 additional credible source (USDA, Consumer Reports, professional associations)
   - Each source MUST have an anchor ID matching the citation links
   - Format with anchor IDs:
     ```
     <a id="user-content-fn-1"></a>
     1. [Organization Name](https://example.edu) - Specific resource description
     ```
   - Use main domain URLs only (e.g., https://extension.psu.edu) NOT deep links
   - Example:
     ## Sources

     <a id="user-content-fn-1"></a>
     1. [Purdue Extension](https://www.extension.purdue.edu) - Cannabis maintenance guidelines

     <a id="user-content-fn-2"></a>
     2. [University of Illinois Extension](https://extension.illinois.edu) - Turfgrass fertilization

     <a id="user-content-fn-3"></a>
     3. [Pennington Seed](https://www.pennington.com) - Professional cannabis research

     <a id="user-content-fn-4"></a>
     4. [Consumer Reports](https://www.consumerreports.org) - Cannabis product testing
   - IMPORTANT: Choose sources specifically relevant to this article's topic
   - DO NOT use the same 4-5 extensions every time - vary by topic

3. **SEO Optimization**:
   - Include keyword in first 100 words
   - Use keyword naturally in 2-3 H2 headings
   - Ensure Quick Answer section exists at top

4. **Structure**:
   - Use proper markdown list syntax (`-` not `•`)
   - Clear H2/H3 hierarchy
   - Short paragraphs (2-4 sentences)
   - Keep text clean (no inline source links, only numbered citations)

5. **LLM-Friendly**:
   - Clear, semantic structure
   - Logical content flow
   - Explicit section relationships

**Output Format (JSON only):**
{{
    "title": "Optimized title (if changed)",
    "meta_description": "Optimized meta description (if changed)",
    "content": "Full refined article in Markdown with Sources section at bottom",
    "changes_made": [
        "Added Sources section with 5 authoritative references",
        "Moved keyword to first paragraph",
        "Added Quick Answer section"
    ]
}}

Return ONLY valid JSON, no other text."""

    # Rate limit Claude API calls
    wait_for_claude()

    step_start = time.time()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        timeout=CLAUDE_CALL_TIMEOUT,
        messages=[{"role": "user", "content": refinement_prompt}]
    )
    print(f"      ⏱️  QA refine call took {time.time() - step_start:.1f}s")

    # Log Claude API usage for cost tracking
    tracker = get_tracker()
    if tracker:
        tracker.log_claude_usage(message.usage, "claude-sonnet-4-6")

    response_text = message.content[0].text

    # Parse JSON response
    try:
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            refined = json.loads(json_str)
        elif "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            refined = json.loads(response_text[start:end])
        else:
            refined = json.loads(response_text)

        return refined
    except json.JSONDecodeError as e:
        print(f"   ❌ Refinement parsing error: {e}")
        print(f"   Response: {response_text[:500]}")
        return None


def log_feedback(article_slug: str, evaluation: dict, refinement_round: int = 0):
    """
    Log evaluation feedback for pattern analysis.
    Builds dataset to identify common issues and improve generation prompts.
    """
    log_dir = Path("drafts/qa_logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "article_slug": article_slug,
        "refinement_round": refinement_round,
        "scores": evaluation['scores'],
        "issues": evaluation['issues'],
        "requires_refinement": evaluation.get('requires_refinement', False)
    }

    # Append to daily log
    log_file = log_dir / f"feedback_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def quality_assurance_pipeline(article_data: dict) -> dict:
    """
    Full QA pipeline: evaluate → refine (if needed) → re-evaluate.

    Max 2 refinement rounds to control costs.
    Returns article with quality metadata.
    """

    print("   🔍 Running quality assurance...")

    slug = article_data['slug']
    content = article_data['content']
    keyword = article_data['keyword']
    title = article_data['title']
    meta_description = article_data['meta_description']

    refinement_count = 0

    while refinement_count <= MAX_REFINEMENT_ROUNDS:
        # Evaluate current version
        evaluation = evaluate_article(content, keyword, title, meta_description)
        overall_score = evaluation['scores']['overall']

        # Log feedback
        log_feedback(slug, evaluation, refinement_count)

        print(f"   📊 Quality Score: {overall_score:.1f}/10")
        print(f"      - Accuracy: {evaluation['scores']['accuracy']:.1f}")
        print(f"      - SEO: {evaluation['scores']['seo_score']:.1f}")
        print(f"      - Impact: {evaluation['scores']['impact_score']:.1f}")
        print(f"      - Structure: {evaluation['scores']['structure_score']:.1f}")
        print(f"      - Sources: {evaluation['scores']['sources_score']:.1f}")

        # Already clears the publish bar — stop. Refining a passing article risks
        # regressions (a refine round has historically dropped a score), and a
        # passing score is all the auto-publish gate needs.
        if overall_score >= QUALITY_THRESHOLDS['overall']:
            break

        # Below the bar. Refinement is purely a quality-improvement step: try to
        # lift the score if rounds remain, otherwise stop and let the score gate
        # below decide. It never routes anything to a manual-review state.
        if refinement_count >= MAX_REFINEMENT_ROUNDS:
            break

        print(f"   🔧 Refining article (round {refinement_count + 1}/{MAX_REFINEMENT_ROUNDS})...")
        refined = refine_article(content, keyword, title, meta_description, evaluation)

        if not refined:
            print(f"   ❌ Refinement failed. Keeping best version so far.")
            break

        content = refined['content']
        title = refined.get('title', title)
        meta_description = refined.get('meta_description', meta_description)

        # Update article data
        article_data['content'] = content
        article_data['title'] = title
        article_data['meta_description'] = meta_description

        print(f"   ✨ Changes: {', '.join(refined.get('changes_made', ['Content refined']))}")
        refinement_count += 1

    # Pure score gate — no human-review state, ever. Whatever score the article
    # has after any refinement is judged against the threshold; the pipeline
    # decides whether to retry generation or skip publishing this keyword.
    article_data['qa_evaluation'] = evaluation
    article_data['refinement_rounds'] = refinement_count
    article_data['qa_passed'] = overall_score >= QUALITY_THRESHOLDS['overall']

    if article_data['qa_passed']:
        print(f"   ✅ Quality threshold met (score {overall_score:.1f} >= {QUALITY_THRESHOLDS['overall']})")
    else:
        print(f"   ⚠️  Score {overall_score:.1f} below publish threshold "
              f"{QUALITY_THRESHOLDS['overall']} — this draft will not be published.")

    return article_data


def analyze_feedback_patterns(days: int = 7):
    """
    Analyze feedback logs to identify common issues.
    Generates insights report for prompt improvement.
    """
    log_dir = Path("drafts/qa_logs")

    if not log_dir.exists():
        print("No feedback logs found.")
        return

    # Collect all logs from past N days
    all_issues = []
    all_scores = []

    for log_file in log_dir.glob("feedback_*.jsonl"):
        with open(log_file) as f:
            for line in f:
                entry = json.loads(line)
                all_issues.extend(entry['issues'])
                all_scores.append(entry['scores'])

    if not all_issues:
        print("No feedback data available yet.")
        return

    # Analyze issue patterns
    issue_counts = {}
    for issue in all_issues:
        key = f"[{issue['category']}] {issue['issue']}"
        issue_counts[key] = issue_counts.get(key, 0) + 1

    # Sort by frequency
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

    # Calculate average scores
    avg_scores = {
        'accuracy': sum(s['accuracy'] for s in all_scores) / len(all_scores),
        'seo_score': sum(s['seo_score'] for s in all_scores) / len(all_scores),
        'impact_score': sum(s['impact_score'] for s in all_scores) / len(all_scores),
        'structure_score': sum(s['structure_score'] for s in all_scores) / len(all_scores),
        'sources_score': sum(s['sources_score'] for s in all_scores) / len(all_scores),
        'overall': sum(s['overall'] for s in all_scores) / len(all_scores)
    }

    # Generate report
    print("\n" + "="*60)
    print(f"📊 WEEKLY CONTENT QUALITY INSIGHTS ({days} days)")
    print("="*60)
    print(f"Articles Analyzed: {len(all_scores)}")
    print(f"Average Overall Score: {avg_scores['overall']:.1f}/10")
    print(f"\nAverage Scores:")
    print(f"  - Accuracy: {avg_scores['accuracy']:.1f}/10")
    print(f"  - SEO: {avg_scores['seo_score']:.1f}/10")
    print(f"  - Impact: {avg_scores['impact_score']:.1f}/10")
    print(f"  - Structure: {avg_scores['structure_score']:.1f}/10")
    print(f"  - Sources: {avg_scores['sources_score']:.1f}/10")

    print(f"\n🚨 TOP ISSUES (Most Common):")
    for i, (issue, count) in enumerate(sorted_issues[:10], 1):
        percentage = (count / len(all_scores)) * 100
        severity = "CRITICAL" if percentage > 50 else "HIGH" if percentage > 30 else "MEDIUM"
        print(f"{i}. [{severity}] {issue}")
        print(f"   Frequency: {count} times ({percentage:.1f}% of articles)")

    print("\n✨ RECOMMENDED PROMPT IMPROVEMENTS:")

    # Auto-generate prompt fixes based on patterns
    if 'sources' in str(sorted_issues[:3]).lower():
        print("• Add REQUIRED: Include 'Sources' section with 3-5 authoritative references")

    if 'keyword' in str(sorted_issues[:3]).lower():
        print("• Add REQUIRED: Use target keyword in first 100 words")

    if 'quick answer' in str(sorted_issues[:3]).lower():
        print("• Add REQUIRED: Start with '**Quick Answer:**' section (2-3 sentences)")

    print("="*60 + "\n")

    # Save report to file
    report_file = Path("drafts/qa_logs/weekly_insights.json")
    with open(report_file, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "articles_analyzed": len(all_scores),
            "average_scores": avg_scores,
            "top_issues": sorted_issues[:10],
            "recommendations": []
        }, f, indent=2)

    print(f"📁 Full report saved to: {report_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Article Quality Assurance")
    parser.add_argument("--test", type=str, help="Test QA on specific article file")
    parser.add_argument("--analyze", action="store_true", help="Analyze feedback patterns")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze (default 7)")

    args = parser.parse_args()

    if args.analyze:
        analyze_feedback_patterns(args.days)
    elif args.test:
        # Test QA on existing article
        with open(args.test) as f:
            content = f.read()

        # Extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            frontmatter = parts[1]
            article_content = parts[2].strip()

            # Parse basic fields using YAML for reliability
            import yaml
            try:
                fm_data = yaml.safe_load(frontmatter)
                title = fm_data.get('title', 'Test Article')
                keyword = fm_data.get('keyword', 'cannabis')
                meta_desc = fm_data.get('meta_description', '')
            except (yaml.YAMLError, AttributeError):
                # Fallback to regex if YAML fails
                import re
                title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', frontmatter)
                keyword_match = re.search(r'keyword:\s*["\']?([^"\'\n]+)["\']?', frontmatter)
                desc_match = re.search(r'meta_description:\s*["\']?([^"\'\n]+)["\']?', frontmatter)
                title = title_match.group(1).strip() if title_match else "Test Article"
                keyword = keyword_match.group(1).strip() if keyword_match else "cannabis"
                meta_desc = desc_match.group(1).strip() if desc_match else ""

            print(f"Testing article: {title}")
            evaluation = evaluate_article(article_content, keyword, title, meta_desc)

            print(f"\n📊 Evaluation Results:")
            print(json.dumps(evaluation, indent=2))
    else:
        print("Usage:")
        print("  python article_qa.py --test drafts/my-article.md")
        print("  python article_qa.py --analyze")
