# The Green Leaf Content Engine

Automated content generation for [strainreport.com](https://strainreport.com).

## Quick Start

```bash
pip install -r requirements.txt
python content_generator.py --keyword "spring cannabis tips"
```

## Documentation

See **[AGENT.md](./AGENT.md)** for complete project documentation including:
- Project structure
- Content workflows (keyword-first & video-first)
- All commands
- Frontmatter schema
- Image standards
- Environment variables
- Cost breakdown

## Required Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
RUNWARE_API_KEY=...
YOUTUBE_API_KEY=AIza...
SUPADATA_API_KEY=...
AMAZON_AFFILIATE_TAG=yourname-20
```

## Pipeline

```
Keyword → Claude AI → Runware Images → YouTube Videos → Affiliates → QA → Publish
```

**Cost per article:** ~$0.10-0.15

## Auto-Generation

GitHub Actions runs Monday & Wednesday at 8am UTC.
