import type { Metadata } from 'next'
import { getSupabase } from '@/lib/supabase'

const baseUrl = 'https://strainreport.com'

export type StrainSeo = { meta_title: string | null; meta_description: string | null }

export type StrainMetaRow = {
  name: string
  strain_type: string | null
  short_description: string | null
  effects: { effect_name: string; effect_type: string }[] | null
  strain_seo: StrainSeo[]
}

/** Unique templated meta description when DB SEO row is missing. */
export function buildStrainMetaDescription(data: StrainMetaRow): string {
  if (data.short_description?.trim()) {
    const trimmed = data.short_description.trim()
    return trimmed.length > 160 ? `${trimmed.slice(0, 157).trimEnd()}...` : trimmed
  }

  const typeLabel = data.strain_type
    ? data.strain_type.charAt(0).toUpperCase() + data.strain_type.slice(1)
    : 'cannabis'
  const positive = (data.effects ?? [])
    .filter((e) => e.effect_type === 'positive')
    .map((e) => e.effect_name)
    .slice(0, 3)
  const effectsPart = positive.length
    ? ` known for ${positive.join(', ').toLowerCase()} effects`
    : ''

  return `${data.name} is a ${typeLabel.toLowerCase()} cannabis strain${effectsPart}. Explore THC/CBD ranges, terpenes, flavors, and growing info on The Strain Report.`
}

export function resolveStrainDescription(data: StrainMetaRow): string {
  const seo = data.strain_seo?.[0]
  return seo?.meta_description?.trim() || buildStrainMetaDescription(data)
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
      .select('name, strain_type, short_description, effects(effect_name, effect_type), strain_seo(meta_title, meta_description)')
      .eq('slug', slug)
      .single()
    data = result.data as unknown as StrainMetaRow
  } catch {
    // env vars unavailable during static build
  }

  if (!data) return {}

  const seo = data.strain_seo?.[0]
  const title = seo?.meta_title ?? `${data.name} Strain | The Strain Report`
  const description = resolveStrainDescription(data)

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
  }
}
