import { COMPARISON_PAIRS } from '@/data/strainComparisonPairs'
import { isThinStrain, getRelatedStrainsMap, type CatalogStrain } from '@/lib/strainCatalog'

/**
 * Single source of truth for which /strains/compare/<a>-vs-<b> URLs we link
 * to and list in sitemap.xml. Shared by sitemap.ts, strain profiles and hubs
 * so every linked comparison is in the sitemap and vice versa.
 */

/** Well-known strains promoted on the homepage, /strains and in compare
 *  pairs. Order = display order. Slugs missing from the catalog are skipped. */
export const POPULAR_STRAIN_SLUGS: string[] = [
  'blue-dream', 'og-kush', 'sour-diesel', 'girl-scout-cookies', 'gelato',
  'wedding-cake', 'granddaddy-purple', 'northern-lights', 'jack-herer',
  'pineapple-express', 'gorilla-glue', 'white-widow', 'green-crack',
  'purple-haze', 'ak-47', 'bubba-kush', 'trainwreck', 'chemdawg',
]

/** Auto-generated comparisons per strain on top of the curated list. */
const AUTO_PAIRS_PER_STRAIN = 2

export type ComparisonPair = { a: string; b: string; slug: string }

const pairKey = (a: string, b: string) => [a, b].sort().join('|')

export function getPopularStrains(catalog: CatalogStrain[], limit = POPULAR_STRAIN_SLUGS.length): CatalogStrain[] {
  const bySlug = new Map(catalog.map((s) => [s.slug, s]))
  return POPULAR_STRAIN_SLUGS.map((slug) => bySlug.get(slug)).filter(Boolean).slice(0, limit) as CatalogStrain[]
}

const memo = new WeakMap<CatalogStrain[], ComparisonPair[]>()

/**
 * Curated COMPARISON_PAIRS (kept in their curated order) plus, for every
 * indexable strain, up to AUTO_PAIRS_PER_STRAIN comparisons against its most
 * related popular strains. Deterministic; one URL per unordered pair.
 * With an empty catalog (no DB env) only the curated pairs are returned.
 */
export function getAllComparisonPairs(catalog: CatalogStrain[]): ComparisonPair[] {
  const cached = memo.get(catalog)
  if (cached) return cached
  const seen = new Set<string>()
  const out: ComparisonPair[] = []
  const add = (a: string, b: string) => {
    if (a === b) return
    const k = pairKey(a, b)
    if (seen.has(k)) return
    seen.add(k)
    out.push({ a, b, slug: `${a}-vs-${b}` })
  }
  const bySlug = new Map(catalog.map((s) => [s.slug, s]))
  const known = (slug: string) => catalog.length === 0 || bySlug.has(slug)
  for (const [a, b] of COMPARISON_PAIRS) if (known(a) && known(b)) add(a, b)

  if (catalog.length) {
    const popular = new Set(getPopularStrains(catalog).filter((s) => !isThinStrain(s)).map((s) => s.slug))
    const related = getRelatedStrainsMap(catalog)
    for (const s of catalog) {
      if (isThinStrain(s)) continue
      // Popular strains ranked by relevance to s (related list first), then catalog order.
      const ranked = [
        ...(related.get(s.slug) ?? []).map((r) => r.slug).filter((x) => popular.has(x)),
        ...POPULAR_STRAIN_SLUGS.filter((x) => popular.has(x)),
      ]
      let added = 0
      for (const p of ranked) {
        if (added >= AUTO_PAIRS_PER_STRAIN) break
        if (p === s.slug) continue
        add(s.slug, p) // an existing (e.g. curated) pair still counts toward the quota
        added++
      }
    }
  }
  memo.set(catalog, out)
  return out
}

/** Comparison pages that include the given strain. */
export function getComparisonPairsForStrain(slug: string, catalog: CatalogStrain[]): ComparisonPair[] {
  return getAllComparisonPairs(catalog).filter((p) => p.a === slug || p.b === slug)
}
