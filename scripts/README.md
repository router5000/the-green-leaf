# Strain fact pipeline

`scripts/enrich_strains.py` (research → draft → `validate_facts.py` gate → apply) and
`scripts/validate_facts.py`. Every fact written to `strains` / `genetics` / `terpenes` /
`effects` must be backed by at least one `strain_sources` row (migration
`site/supabase/migrations/004_strain_sources.sql`); drafts with an unsourced fact are
rejected and nothing is written.

```bash
python scripts/enrich_strains.py --slug lava-cake                 # research mode, dry run
python scripts/enrich_strains.py --slug lava-cake --correct-types # allow sourced type fixes
python scripts/enrich_strains.py --from-file drafts.json          # gate pre-made drafts (dry run)
python scripts/enrich_strains.py --from-file drafts.json --apply  # write passing drafts + sources
```

`--apply` needs `SUPABASE_URL` and `SUPABASE_SECRET_KEY`. `--from-file` exits 1 if any entry was rejected.
Reports go to `.logs/run_reports/`.

## `--from-file` draft JSON schema

A list of entries (or one entry, or `{"drafts": [...]}`):

```jsonc
[
  {
    "slug": "lava-cake",                 // required, existing strains.slug
    "stored_strain_type": "hybrid",      // optional, used only when Supabase is not configured (dry run)
    "draft": {                           // required; every key optional, unknown keys are rejected
      "short_description": "…",          // backed by field "short_description" or "description"
      "description": "…",                // field "description"
      "aka": ["…"],                      // field "aka"
      "flavors": ["…"], "aromas": ["…"], "colors": ["…"],   // fields "flavors" / "aromas" / "colors"
      "genetics": [{"parent_strain_name": "Thin Mint GSC", "parent_type": "mother"}],  // "genetics"; parent_type mother|father only
      "terpenes": [{"terpene_name": "Caryophyllene", "percentage": null}],              // "terpenes" (percentages need "terpene_pct" to show on the site)
      "effects":  [{"effect_name": "Relaxed", "effect_type": "positive", "intensity": 3}], // "effects"; positive|negative only
      "origin_country": "USA",           // "origin_country"
      "strain_type": "indica",           // "strain_type"; differing from the stored type = a correction (below)
      "thc_reported": [20, 24]           // [min, max] -> thc_min/thc_max; field "thc"
    },
    "sources": [                         // one row per (field, page) -> strain_sources
      {
        "field": "genetics",             // required, a strain_sources.field value
        "url": "https://www.leafly.com/strains/lava-cake",   // required (or "source_url"); deep page, not a homepage
        "value": "Thin Mint GSC x Grape Pie",                // optional: the value this source supports
        "source_name": "Leafly",         // optional, derived from the domain if omitted
        "quote": "verbatim <=300 chars", // optional
        "retrieved_at": "2026-11-02"     // optional (alias "fetched_at"), defaults to now()
      }
    ]
  }
]
```

Rules enforced before anything is written:

- every non-empty draft key needs ≥1 source whose `field` backs it (table above);
- source URLs must be deep `http(s)` pages; `genetics.parent_type` must be `mother`/`father`;
- **strain_type correction**: if `draft.strain_type` differs from the stored type it is applied only
  with `strain_type` sources on ≥2 distinct domains and prose that does not state another type;
  otherwise the entry is rejected as a `type conflict`;
- on `--apply`, sources are inserted into `strain_sources` (duplicates on
  `(strain_id, field, source_url)` are ignored). Existing grow fields are never written.

## Display gating

Strain pages hide grow fields (`flowering_time_days`, `yield_*`, `height_*`, `difficulty`) and
terpene percentages unless `strain_sources` has a row with that column name as `field`
(`terpene_pct` for percentages). The DB values are kept. See `site/src/lib/sourcedFields.ts`.
