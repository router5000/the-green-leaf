-- 004: provenance for strain facts (fact-quality overhaul).
-- NOT applied automatically. Apply in the Supabase SQL editor / `supabase db push`
-- before running scripts/enrich_strains.py --apply.

CREATE TABLE IF NOT EXISTS strain_sources (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strain_id   uuid NOT NULL REFERENCES strains(id) ON DELETE CASCADE,
  field       text NOT NULL,          -- description | thc | aka | flavors | effects | genetics | ...
  url         text NOT NULL,
  quote       text,                   -- verbatim snippet (<= 300 chars) supporting the field
  fetched_at  timestamptz NOT NULL DEFAULT now(),
  created_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT strain_sources_url_not_homepage CHECK (url ~ '^https?://[^/]+/.+')
);

CREATE INDEX IF NOT EXISTS idx_strain_sources_strain ON strain_sources(strain_id);
CREATE INDEX IF NOT EXISTS idx_strain_sources_field  ON strain_sources(strain_id, field);

ALTER TABLE strain_sources ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "strain_sources public read" ON strain_sources;
CREATE POLICY "strain_sources public read" ON strain_sources FOR SELECT USING (true);

GRANT ALL    ON public.strain_sources TO service_role;
GRANT SELECT ON public.strain_sources TO anon, authenticated;

-- Stop new medical effect rows. Existing rows are left in place; remove them
-- deliberately (review first) with:
--   DELETE FROM effects WHERE effect_type = 'medical';
-- after which this constraint can be added:
--   ALTER TABLE effects DROP CONSTRAINT IF EXISTS effects_effect_type_check;
--   ALTER TABLE effects ADD CONSTRAINT effects_effect_type_check
--     CHECK (effect_type IN ('positive', 'negative'));
