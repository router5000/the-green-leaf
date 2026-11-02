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
/** Max auto pairings any single popular strain takes part in. */
const AUTO_PAIRS_PER_POPULAR = 15
/** Max compare links rendered on one strain page. */
export const COMPARE_LINKS_PER_PAGE = 8

export type ComparisonPair = { a: string; b: string; slug: string; curated: boolean }

const pairKey = (a: string, b: string) => [a, b].sort().join('|')

const VARIANT_SUFFIX = /-(auto|autoflower|automatic|fast|cbd|x|bx\d*|s\d*|\d+)$/
const baseSlug = (slug: string) => {
  let b = slug
  while (VARIANT_SUFFIX.test(b)) b = b.replace(VARIANT_SUFFIX, '')
  return b
}
/** True for parent/variant pairs like blue-dream-auto vs blue-dream. */
export function isVariantPair(a: string, b: string): boolean {
  return a.startsWith(`${b}-`) || b.startsWith(`${a}-`) || baseSlug(a) === baseSlug(b)
}

function hash(s: string): number {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619)
  return h >>> 0
}

export function getPopularStrains(catalog: CatalogStrain[], limit = POPULAR_STRAIN_SLUGS.length): CatalogStrain[] {
  const bySlug = new Map(catalog.map((s) => [s.slug, s]))
  return POPULAR_STRAIN_SLUGS.map((slug) => bySlug.get(slug)).filter(Boolean).slice(0, limit) as CatalogStrain[]
}

const memo = new WeakMap<CatalogStrain[], ComparisonPair[]>()

/**
 * Curated COMPARISON_PAIRS (always kept) plus auto pairs: each indexable
 * strain gets up to AUTO_PAIRS_PER_STRAIN comparisons against popular strains
 * of the SAME type (most related first), skipping variant pairs, with each
 * popular strain capped at AUTO_PAIRS_PER_POPULAR auto pairings. Strains are
 * processed in a stable hashed order so the cap isn't spent alphabetically.
 * Deterministic; one URL per unordered pair. Empty catalog => curated only.
 */
export function getAllComparisonPairs(catalog: CatalogStrain[]): ComparisonPair[] {
  const cached = memo.get(catalog)
  if (cached) return cached
  const seen = new Set<string>()
  const out: ComparisonPair[] = []
  const add = (a: string, b: string, curated: boolean) => {
    if (a === b) return false
    const k = pairKey(a, b)
    if (seen.has(k)) return false
    seen.add(k)
    out.push({ a, b, slug: `${a}-vs-${b}`, curated })
    return true
  }
  const bySlug = new Map(catalog.map((s) => [s.slug, s]))
  const known = (slug: string) => catalog.length === 0 || bySlug.has(slug)
  for (const [a, b] of COMPARISON_PAIRS) if (known(a) && known(b)) add(a, b, true)

  if (catalog.length) {
    const popular = getPopularStrains(catalog).filter((s) => !isThinStrain(s))
    const popularSet = new Set(popular.map((s) => s.slug))
    const used = new Map(popular.map((s) => [s.slug, 0]))
    const related = getRelatedStrainsMap(catalog)
    const order = catalog
      .filter((s) => !isThinStrain(s))
      .sort((x, y) => hash(x.slug) - hash(y.slug) || x.slug.localeCompare(y.slug))
    for (const s of order) {
      const sameType = (slug: string) => bySlug.get(slug)?.strain_type === s.strain_type
      const ranked = [
        ...(related.get(s.slug) ?? []).map((r) => r.slug).filter((x) => popularSet.has(x)),
        ...popular.map((p) => p.slug),
      ]
      let added = 0
      for (const p of new Set(ranked)) {
        if (added >= AUTO_PAIRS_PER_STRAIN) break
        if (p === s.slug || !sameType(p) || isVariantPair(s.slug, p)) continue
        if (seen.has(pairKey(s.slug, p))) { added++; continue }
        if ((used.get(p) ?? 0) >= AUTO_PAIRS_PER_POPULAR) continue
        // a popular strain on the s side also spends its own quota
        if (popularSet.has(s.slug) && (used.get(s.slug) ?? 0) >= AUTO_PAIRS_PER_POPULAR) break
        add(s.slug, p, false)
        used.set(p, (used.get(p) ?? 0) + 1)
        if (popularSet.has(s.slug)) used.set(s.slug, (used.get(s.slug) ?? 0) + 1)
        added++
      }
    }
  }
  memo.set(catalog, out)
  return out
}

/**
 * Compare links for one strain page: curated first, then pairs where this
 * strain is the non-popular side (so every auto pair is linked from at least
 * one page), then the rest — capped at COMPARE_LINKS_PER_PAGE.
 */
export function getComparisonPairsForStrain(slug: string, catalog: CatalogStrain[]): ComparisonPair[] {
  const mine = getAllComparisonPairs(catalog).filter((p) => p.a === slug || p.b === slug)
  const rank = (p: ComparisonPair) => (p.curated ? 0 : p.a === slug ? 1 : 2)
  return [...mine].sort((x, y) => rank(x) - rank(y)).slice(0, COMPARE_LINKS_PER_PAGE)
}
