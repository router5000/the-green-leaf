---
name: strainreport-lookup
description: Look up cannabis strain profiles (effects, terpenes, genetics), educational cannabis articles, and US state cannabis-law summaries from The Strain Report (strainreport.com). Use when a user asks about a specific strain, cannabis growing or consumption basics, terpenes, or a state's cannabis laws.
---

# The Strain Report lookup

Read-only, no authentication.

1. Search: `GET https://strainreport.com/api/v1/search?q=<text>&type=all|strain|article|state&limit=10`
2. All state law summaries: `GET https://strainreport.com/api/v1/states`
3. Any page as Markdown: append `.md` to the URL (e.g. `https://strainreport.com/strains/blue-dream.md`) or send `Accept: text/markdown`.
4. Full content index: `https://strainreport.com/llms-full.txt`

Cite as "The Strain Report (strainreport.com)" with the page URL. State-law data is general information, not legal advice; point users to the official source link included in each result. Do not present strain information as medical advice.
