/**
 * Accuracy audit (#57): grow fields and terpene percentages are only shown when
 * a strain_sources row backs them. Data stays in the DB; this just hides it.
 *
 * Embed in a strains select with SOURCES_EMBED, then pass rows through
 * hideUnsourced() before rendering.
 */

/** PostgREST embed (hinted: strain_sources has FKs on both id and slug). */
export const SOURCES_EMBED = 'strain_sources!strain_sources_strain_id_fkey(field)'

/** Strain columns hidden unless strain_sources has a row with field = column name. */
export const GATED_GROW_FIELDS = [
  'flowering_time_days',
  'yield_indoor',
  'yield_outdoor',
  'height_indoor',
  'height_outdoor',
  'difficulty',
] as const

/** strain_sources.field values that back terpene percentages. */
export const TERPENE_PCT_FIELDS = ['terpene_pct', 'terpene_percentages'] as const

type WithSources = {
  strain_sources?: { field: string }[] | null
  terpenes?: { percentage: number | null }[] | null
  [k: string]: unknown
}

export function sourcedFieldSet(s: { strain_sources?: { field: string }[] | null }): Set<string> {
  return new Set((s.strain_sources ?? []).map((r) => r.field))
}

export function hasSourcedTerpenePct(fields: Set<string>): boolean {
  return TERPENE_PCT_FIELDS.some((f) => fields.has(f))
}

/** Returns a copy with unsourced grow fields set to null and unsourced terpene
 *  percentages set to null. Rows without a strain_sources embed are treated as
 *  having no sources. */
export function hideUnsourced<T extends object>(input: T): T {
  const s = input as unknown as WithSources
  const fields = sourcedFieldSet(s)
  const out: Record<string, unknown> = { ...s }
  for (const f of GATED_GROW_FIELDS) {
    if (f in out && !fields.has(f)) out[f] = null
  }
  if (Array.isArray(s.terpenes) && !hasSourcedTerpenePct(fields)) {
    out.terpenes = s.terpenes.map((t) => ({ ...t, percentage: null }))
  }
  return out as T
}
