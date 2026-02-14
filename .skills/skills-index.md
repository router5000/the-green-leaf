# Skills Index

A portable index of custom skills for use across projects. Copy this entire `skills-bundle` folder to any project and rename to `.skills`.

---

## Available Skills

| Skill ID | Name | Folder | Description |
|----------|------|--------|-------------|
| `skill-code-review` | Frontend Code Review | `skill-code-review/` | Review frontend files (.tsx, .ts, .js) for code quality, performance, and business logic issues |
| `skill-design` | Frontend Design | `skill-design/` | Create distinctive, production-grade frontend interfaces with high design quality |
| `skill-testing` | Frontend Testing | `skill-testing/` | Generate Vitest + React Testing Library tests for frontend components, hooks, and utilities |
| `skill-prompts` | Prompt Engineering Patterns | `skill-prompts/` | Master advanced prompt engineering techniques for LLM performance, reliability, and controllability |
| `skill-seo` | SEO Review | `skill-seo/` | Perform focused SEO audits to maximize search visibility and featured snippet optimization |

---

## Skill Details

### skill-code-review
**Folder:** `skills/skill-code-review/`
**Trigger:** When user requests review of frontend files (.tsx, .ts, .js)

**Capabilities:**
- Pending-change reviews (staged/working-tree files)
- File-targeted reviews
- Code quality checks
- Performance analysis
- Business logic validation

**References:**
- `references/code-quality.md`
- `references/performance.md`
- `references/business-logic.md`

---

### skill-design
**Folder:** `skills/skill-design/`
**Trigger:** When user asks to build web components, pages, or applications

**Capabilities:**
- Production-grade frontend interfaces
- Bold aesthetic direction (brutalist, minimalist, retro-futuristic, etc.)
- Typography, color, motion, and spatial composition guidance
- Avoids generic "AI slop" aesthetics

**Key Principles:**
- Choose distinctive fonts (avoid Arial, Inter, Roboto)
- Commit to cohesive color themes
- Use meaningful animations and micro-interactions
- Create unexpected layouts with asymmetry and overlap

---

### skill-testing
**Folder:** `skills/skill-testing/`
**Trigger:** Testing, spec files, coverage, Vitest, RTL, unit tests, integration tests

**Tech Stack:**
- Vitest 4.0.16
- React Testing Library 16.0
- jsdom
- nock 14.0
- TypeScript 5.x

**Key Commands:**
```bash
pnpm test              # Run all tests
pnpm test:watch        # Watch mode
pnpm test:coverage     # Generate coverage
pnpm analyze-component # Analyze complexity
```

**References:**
- `references/mocking.md`
- `references/async-testing.md`
- `references/domain-components.md`
- `references/common-patterns.md`
- `references/checklist.md`
- `references/workflow.md`

---

### skill-prompts
**Folder:** `skills/skill-prompts/`
**Trigger:** Optimizing prompts, improving LLM outputs, designing production prompt templates

**Capabilities:**
- Few-shot learning (example selection, diversity sampling)
- Chain-of-thought prompting (step-by-step reasoning)
- Prompt optimization (A/B testing, iteration workflows)
- Template systems (variable interpolation, conditional sections)
- System prompt design (behavior constraints, output formats)

**Key Patterns:**
- Progressive disclosure (simple → complex)
- Instruction hierarchy: System → Task → Examples → Input → Output
- Error recovery with fallback instructions

**References:**
- `references/few-shot-learning.md`
- `references/chain-of-thought.md`
- `references/prompt-optimization.md`
- `references/prompt-templates.md`
- `references/system-prompts.md`
- `assets/prompt-template-library.md`

---

### skill-seo
**Folder:** `skills/skill-seo/`
**Trigger:** Before publishing, optimizing underperforming pages, content audits

**Audit Categories (30 points total):**
- Title Tag (4 pts): 50-60 chars, keyword placement, hook
- Meta Description (4 pts): 150-160 chars, action word, value proposition
- Keyword Placement (5 pts): Title, description, first 100 words, H2
- Content Structure (6 pts): Question hook, early code, Info box, 1500+ words
- Featured Snippets (4 pts): 40-60 word definitions, numbered steps, tables
- Internal Linking (4 pts): 3-5 links, descriptive anchors, Related Concepts
- Technical SEO (3 pts): Single H1, keyword in URL, no orphan pages

**Score Interpretation:**
- 27-30 (90-100%): Excellent - Ready to publish
- 23-26 (75-89%): Good - Minor optimizations needed
- 17-22 (55-74%): Fair - Several improvements needed
- 0-16 (<55%): Poor - Significant work required

---

## Installation

1. Copy the entire `skills-bundle` folder to your project root
2. Rename to `.skills`:
   ```bash
   cp -r skills-bundle /path/to/your/project/.skills
   ```

Your project structure should look like:
```
your-project/
├── .skills/
│   ├── skills-index.md
│   └── skills/
│       ├── skill-code-review/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── skill-design/
│       │   └── SKILL.md
│       ├── skill-testing/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── skill-prompts/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   └── assets/
│       └── skill-seo/
│           └── SKILL.md
├── src/
└── ...
```

---

## Quick Reference

| Task | Use Skill |
|------|-----------|
| Review my React code | `skill-code-review` |
| Build a landing page | `skill-design` |
| Write tests for components | `skill-testing` |
| Optimize my prompts | `skill-prompts` |
| Audit page for SEO | `skill-seo` |
