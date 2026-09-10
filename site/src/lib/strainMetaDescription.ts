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
