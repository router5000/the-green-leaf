-- 004: provenance for strain facts (accuracy audit, #57).
-- Applied 2026-11-02 via Supabase migration "strain_sources".
-- One row per (strain, field, source). `field` names the strain column / child table
-- the source backs (description | short_description | strain_type | thc | genetics |
-- flavors | aromas | aka | effects | terpenes | terpene_pct | flowering_time_days |
-- yield_indoor | yield_outdoor | height_indoor | height_outdoor | difficulty | ...).
-- Strain pages show grow fields and terpene percentages only when a row backs them.

CREATE TABLE IF NOT EXISTS public.strain_sources (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strain_id    uuid NOT NULL REFERENCES public.strains(id) ON DELETE CASCADE,
  slug         text NOT NULL REFERENCES public.strains(slug) ON UPDATE CASCADE ON DELETE CASCADE,
  field        text NOT NULL,
  value        text,                       -- the value the source supports (as stored/applied)
  source_url   text NOT NULL,
  source_name  text,                       -- e.g. Leafly, AllBud, breeder site
  quote        text,                       -- verbatim snippet (<= 300 chars)
  retrieved_at timestamptz NOT NULL DEFAULT now(),
  created_at   timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT strain_sources_url_not_homepage CHECK (source_url ~ '^https?://[^/]+/.+'),
  CONSTRAINT strain_sources_unique UNIQUE (strain_id, field, source_url)
);

CREATE INDEX IF NOT EXISTS idx_strain_sources_strain_field ON public.strain_sources(strain_id, field);
CREATE INDEX IF NOT EXISTS idx_strain_sources_slug ON public.strain_sources(slug);

ALTER TABLE public.strain_sources ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read on strain_sources" ON public.strain_sources;
CREATE POLICY "Allow public read on strain_sources" ON public.strain_sources
  FOR SELECT TO anon, authenticated USING (true);

GRANT ALL    ON public.strain_sources TO service_role;
GRANT SELECT ON public.strain_sources TO anon, authenticated;
