-- strains (core table)
CREATE TABLE strains (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug                text NOT NULL UNIQUE,
  name                text NOT NULL,
  aka                 text[],
  strain_type         text NOT NULL CHECK (strain_type IN ('indica', 'sativa', 'hybrid')),
  thc_min             numeric(5,2),
  thc_max             numeric(5,2),
  cbd_min             numeric(5,2),
  cbd_max             numeric(5,2),
  description         text,
  short_description   text,
  flavors             text[],
  aromas              text[],
  colors              text[],
  difficulty          text CHECK (difficulty IN ('easy', 'moderate', 'difficult')),
  flowering_time_days integer,
  yield_indoor        text,
  yield_outdoor       text,
  height_indoor       text,
  height_outdoor      text,
  origin_country      text,
  published           boolean NOT NULL DEFAULT false,
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);

-- effects
CREATE TABLE effects (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strain_id   uuid NOT NULL REFERENCES strains(id) ON DELETE CASCADE,
  effect_name text NOT NULL,
  effect_type text NOT NULL CHECK (effect_type IN ('positive', 'negative', 'medical')),
  intensity   integer CHECK (intensity BETWEEN 1 AND 5)
);

-- terpenes
CREATE TABLE terpenes (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strain_id    uuid NOT NULL REFERENCES strains(id) ON DELETE CASCADE,
  terpene_name text NOT NULL,
  percentage   numeric(5,3)
);

-- genetics
CREATE TABLE genetics (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strain_id          uuid NOT NULL REFERENCES strains(id) ON DELETE CASCADE,
  parent_strain_name text NOT NULL,
  parent_type        text NOT NULL CHECK (parent_type IN ('mother', 'father'))
);

-- strain_seo
CREATE TABLE strain_seo (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strain_id        uuid NOT NULL UNIQUE REFERENCES strains(id) ON DELETE CASCADE,
  meta_title       text,
  meta_description text,
  focus_keyword    text,
  og_image_url     text
);

-- Indexes
CREATE INDEX idx_strains_slug        ON strains(slug);
CREATE INDEX idx_strains_strain_type ON strains(strain_type);
CREATE INDEX idx_strains_published   ON strains(published);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER strains_updated_at
  BEFORE UPDATE ON strains
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
