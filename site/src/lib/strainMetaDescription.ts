import type { Metadata } from 'next'
import { getSupabase } from '@/lib/supabase'
import { getStrainCatalogSafe, isThinStrain } from '@/lib/strainCatalog'
import { buildStrainDescription, buildStrainTitle, DESC_MIN, DESC_MAX } from '@/lib/strainSeoText'
import { hideUnsourced, SOURCES_EMBED } from '@/lib/sourcedFields'

const baseUrl = 'https://strainreport.com'

export type StrainSeo = { meta_title: string | null; meta_description: string | null }

export type StrainMetaRow = {
  name: string
  strain_type: string | null
  short_description: string | null
  thc_min?: number | null
  thc_max?: number | null
  flavors?: string[] | null
  effects: { effect_name: string; effect_type: string }[] | null
  terpenes?: { terpene_name: string; percentage: number | null }[] | null
  // PostgREST returns an object for a one-to-one embed and an array otherwise.
  strain_seo: StrainSeo[] | StrainSeo | null
}

/** Unique, data-driven meta description (140–158 chars, never cut mid-word). */
export function buildStrainMetaDescription(data: StrainMetaRow): string {
  return buildStrainDescription(data)
}

export function strainSeoRow(data: Pick<StrainMetaRow, 'strain_seo'>): StrainSeo | null {
  const v = data.strain_seo
  return (Array.isArray(v) ? v[0] : v) ?? null
}

/**
 * A curated DB meta_description wins only when it is already DESC_MIN–DESC_MAX
 * chars and ends on a full sentence; otherwise we build one from the strain's data.
 */
export function resolveStrainDescription(data: StrainMetaRow): string {
  const seo = strainSeoRow(data)?.meta_description?.trim()
  if (seo && seo.length >= DESC_MIN && seo.length <= DESC_MAX && /[.!?]$/.test(seo)) return seo
  return buildStrainMetaDescription(data)
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  let data: StrainMetaRow | null = null
  try {
    const result = await getSupabase()
      .from('strains')
      .select('name, strain_type, short_description, thc_min, thc_max, flavors, effects(effect_name, effect_type), terpenes(terpene_name, percentage), strain_seo(meta_title, meta_description), ' + SOURCES_EMBED)
      .eq('slug', slug)
      .single()
    const row = (result as unknown as { data: StrainMetaRow | null }).data
    data = row ? hideUnsourced(row) : null
  } catch {
    // env vars unavailable during static build
  }

  if (!data) return {}

  // Uniform, unique title format for every strain (DB meta_title is not used:
  // the old fallback "<Name> Strain | The Strain Report" was generic).
  const title = buildStrainTitle(data.name)
  const description = resolveStrainDescription(data)

  // Thin-page gate: below THIN_STRAIN_WORD_THRESHOLD visible words the
  // profile stays live and linked but is kept out of the index.
  const catalogRow = (await getStrainCatalogSafe()).find((c) => c.slug === slug)
  const thin = catalogRow ? isThinStrain(catalogRow) : false

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `${baseUrl}/strains/${slug}`,
      siteName: 'The Strain Report',
      type: 'website',
    },
    twitter: { card: 'summary_large_image', title, description },
    alternates: { canonical: `${baseUrl}/strains/${slug}` },
    ...(thin ? { robots: { index: false, follow: true } } : {}),
  }
}
