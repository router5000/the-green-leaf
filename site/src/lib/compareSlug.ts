/**
 * Canonical /strains/compare/<a>-vs-<b> slug helpers.
 * Direction is alphabetical by slug (localeCompare), matching pairKey()
 * uniqueness in strainComparisons.ts. One URL per unordered pair; the
 * reverse 301s here (see proxy.ts) and is never linked or sitemapped.
 */

export function parseCompareSlug(slug: string): [string, string] | null {
  const parts = slug.split('-vs-')
  if (parts.length !== 2) return null
  const [a, b] = parts
  if (!a || !b || a === b) return null
  return [a, b]
}

/** Canonical compare slug: alphabetical order, e.g. blue-dream-vs-og-kush. */
export function canonicalCompareSlug(a: string, b: string): string {
  const [left, right] = a.localeCompare(b) <= 0 ? [a, b] : [b, a]
  return `${left}-vs-${right}`
}

export function comparePath(a: string, b: string): string {
  return `/strains/compare/${canonicalCompareSlug(a, b)}`
}

/** Canonical slug for a pair URL, or null if the slug isn't a valid pair. */
export function canonicalizeCompareSlug(slug: string): string | null {
  const pair = parseCompareSlug(slug)
  if (!pair) return null
  return canonicalCompareSlug(pair[0], pair[1])
}
