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
