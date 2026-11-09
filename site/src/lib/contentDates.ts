/**
 * Template "last changed" dates, computed from git history at build time in
 * next.config.js (inlined via `env.CONTENT_DATES`). Used for sitemap lastmod
 * so a page's date reflects the later of its data update and its template
 * change, instead of a hardcoded constant. Missing groups fall back to the
 * build date.
 */
export type ContentDateGroup =
  | 'strain' | 'strainHub' | 'compare' | 'states' | 'terpenes' | 'home'
  | 'about' | 'contact' | 'privacy' | 'terms' | 'affiliate' | 'videos' | 'topics' | 'articles'

type Raw = Partial<Record<ContentDateGroup | 'build', string>>

function parse(): Raw {
  try {
    return JSON.parse(process.env.CONTENT_DATES ?? '{}') as Raw
  } catch {
    return {}
  }
}

const RAW = parse()
const BUILD = toDate(RAW.build) ?? new Date()

function toDate(v: string | null | undefined): Date | null {
  if (!v) return null
  const d = new Date(v)
  return isNaN(d.getTime()) ? null : d
}

export function templateDate(group: ContentDateGroup): Date {
  return toDate(RAW[group]) ?? BUILD
}

/** Newest valid date among the inputs (strings, Dates, null). */
export function latestDate(...inputs: (Date | string | null | undefined)[]): Date {
  const ds = inputs.map((x) => (x instanceof Date ? x : toDate(x))).filter((d): d is Date => !!d && !isNaN(d.getTime()))
  return ds.length ? new Date(Math.max(...ds.map((d) => d.getTime()))) : BUILD
}

/** Strain row fields needed to decide a trustworthy content-change date. */
export type StrainDateFields = {
  created_at?: string | null
  updated_at?: string | null
}

/**
 * Real last-content-change timestamp for a strain, or null when we only have
 * the seed insert (created_at ≈ updated_at). Never invents freshness: seed-only
 * rows return null so the UI can hide "Updated" and JSON-LD can omit
 * dateModified. Pipeline writes bump updated_at via the strains trigger (and
 * an explicit patch), so enriched pages return that ISO time.
 */
export function strainContentUpdatedAt(s: StrainDateFields): string | null {
  const updated = toDate(s.updated_at)
  if (!updated) return null
  const created = toDate(s.created_at)
  // Insert sets both columns to now(); ignore sub-minute trigger jitter.
  if (created && updated.getTime() - created.getTime() <= 60_000) return null
  return updated.toISOString()
}

/** Deterministic UTC label so SSR and hydration agree. */
export function formatContentDate(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  })
}
