import { getSupabase } from '@/lib/supabase'

/**
 * Site-wide strain catalog used for internal linking (related strains, linked
 * parent genetics, A–Z index) and the thin-page gate (noindex + sitemap
 * exclusion). One query loads every published strain with its child rows;
 * the result is memoised per server instance so ISR/static builds of 340
 * strain pages don't each re-download the catalog.
 */

/** Strains whose visible profile content is below this many words get
 *  `noindex,follow` and are left out of sitemap.xml (they stay live and
 *  linked). Mirrors the lawncare-center thin-page rule. */
export const THIN_STRAIN_WORD_THRESHOLD = 300

/** Fixed lastModified for pages with no content date of their own. Bump when
 *  those templates change materially. */
export const STATIC_CONTENT_LASTMOD = new Date('2026-10-19')

export type CatalogStrain = {
  id: string
  name: string
  slug: string
  aka: string[] | null
  strain_type: string
  description: string | null
  short_description: string | null
  flavors: string[] | null
  aromas: string[] | null
  colors: string[] | null
  origin_country: string | null
  difficulty: string | null
  yield_indoor: string | null
  yield_outdoor: string | null
  height_indoor: string | null
  height_outdoor: string | null
  updated_at: string | null
  effects: { effect_name: string; effect_type: string }[] | null
  terpenes: { terpene_name: string; percentage: number | null }[] | null
  genetics: { parent_strain_name: string; parent_type: string }[] | null
}

const SELECT = `id, name, slug, aka, strain_type, description, short_description,
  flavors, aromas, colors, origin_country, difficulty, yield_indoor, yield_outdoor,
  height_indoor, height_outdoor, updated_at,
  effects(effect_name, effect_type), terpenes(terpene_name, percentage),
  genetics(parent_strain_name, parent_type)`

const TTL_MS = 10 * 60 * 1000
let memo: { at: number; p: Promise<CatalogStrain[]> } | null = null

export function getStrainCatalog(): Promise<CatalogStrain[]> {
  if (memo && Date.now() - memo.at < TTL_MS) return memo.p
  const p = (async () => {
    const { data, error } = await getSupabase()
      .from('strains')
      .select(SELECT)
      .eq('published', true)
      .order('name', { ascending: true })
    if (error) throw error
    return (data as unknown as CatalogStrain[]) ?? []
  })()
  memo = { at: Date.now(), p }
  p.catch(() => { memo = null })
  return p
}

/** Catalog, or [] when Supabase env is unavailable (logged, not thrown). */
export async function getStrainCatalogSafe(): Promise<CatalogStrain[]> {
  try {
    return await getStrainCatalog()
  } catch (err) {
    console.error('[strainCatalog] failed to load catalog:', err)
    return []
  }
}

// ── Thin-page gate ─────────────────────────────────────────────────────────

function words(s: string | null | undefined): number {
  if (!s) return 0
  const t = s.trim()
  return t ? t.split(/\s+/).length : 0
}

/** Words of strain-specific content rendered on /strains/<slug> (name, AKA,
 *  short description, overview, effect/terpene/genetics/flavor chips, grow
 *  stats). Template chrome and JSON-LD are excluded on purpose. */
export function visibleWordCount(s: CatalogStrain): number {
  let n = words(s.name) + words(s.short_description) + words(s.description)
  for (const a of s.aka ?? []) n += words(a)
  for (const e of s.effects ?? []) n += words(e.effect_name)
  for (const t of s.terpenes ?? []) n += words(t.terpene_name)
  for (const g of s.genetics ?? []) n += words(g.parent_strain_name)
  for (const x of [...(s.flavors ?? []), ...(s.aromas ?? []), ...(s.colors ?? [])]) n += words(x)
  for (const x of [s.origin_country, s.difficulty, s.yield_indoor, s.yield_outdoor, s.height_indoor, s.height_outdoor]) n += words(x)
  return n
}

export function isThinStrain(s: CatalogStrain): boolean {
  return visibleWordCount(s) < THIN_STRAIN_WORD_THRESHOLD
}

// ── Name → slug resolution (parent genetics links) ─────────────────────────

export function normalizeStrainName(name: string): string {
  return name
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[#'’".]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

export function buildNameIndex(catalog: CatalogStrain[]): Map<string, string> {
  const m = new Map<string, string>()
  for (const s of catalog) {
    m.set(normalizeStrainName(s.name), s.slug)
    m.set(normalizeStrainName(s.slug.replace(/-/g, ' ')), s.slug)
    for (const a of s.aka ?? []) {
      const k = normalizeStrainName(a)
      if (k && !m.has(k)) m.set(k, s.slug)
    }
  }
  return m
}

export function resolveStrainSlug(name: string, index: Map<string, string>): string | null {
  return index.get(normalizeStrainName(name)) ?? null
}

// ── Related strains ────────────────────────────────────────────────────────

export const RELATED_STRAIN_COUNT = 8

function hash(s: string): number {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619)
  return h >>> 0
}

/**
 * Deterministic related strains: parent/child genetics links score highest,
 * then shared parents, shared terpenes, shared positive effects, and same
 * type. Ties break on a stable hash of the slug pair so links spread across
 * the catalog (rather than always favouring alphabetically-first strains),
 * which keeps every strain reachable from other strain pages.
 */
function rankRelated(target: CatalogStrain, catalog: CatalogStrain[], index: Map<string, string>): CatalogStrain[] {
  const parentSlugs = new Set(
    (target.genetics ?? []).map((g) => resolveStrainSlug(g.parent_strain_name, index)).filter(Boolean) as string[],
  )
  const parentNames = new Set((target.genetics ?? []).map((g) => normalizeStrainName(g.parent_strain_name)))
  const terps = new Set((target.terpenes ?? []).map((t) => t.terpene_name.toLowerCase()))
  const effects = new Set(
    (target.effects ?? []).filter((e) => e.effect_type === 'positive').map((e) => e.effect_name.toLowerCase()),
  )
  const targetKey = normalizeStrainName(target.name)

  const scored = catalog
    .filter((c) => c.slug !== target.slug)
    .map((c) => {
      let score = 0
      if (parentSlugs.has(c.slug)) score += 50
      const cParents = (c.genetics ?? []).map((g) => normalizeStrainName(g.parent_strain_name))
      if (cParents.includes(targetKey)) score += 40 // c is a child of target
      score += cParents.filter((p) => parentNames.has(p)).length * 12 // siblings
      score += (c.terpenes ?? []).filter((t) => terps.has(t.terpene_name.toLowerCase())).length * 3
      score += (c.effects ?? []).filter((e) => e.effect_type === 'positive' && effects.has(e.effect_name.toLowerCase())).length * 2
      if (c.strain_type === target.strain_type) score += 6
      return { c, score, tie: hash(`${target.slug}|${c.slug}`) }
    })
    .sort((a, b) => b.score - a.score || a.tie - b.tie)

  return scored.map((x) => x.c)
}

/** Slots per page filled purely by relevance; the rest go to relevant-but-
 *  under-linked strains so no profile is left without inbound strain links. */
const RELEVANCE_SLOTS = 6
const DISCOVERY_POOL = 40

const relatedMemo = new WeakMap<CatalogStrain[], Map<string, CatalogStrain[]>>()

/** Related strains for every slug, computed in one deterministic pass. */
export function getRelatedStrainsMap(catalog: CatalogStrain[]): Map<string, CatalogStrain[]> {
  const cached = relatedMemo.get(catalog)
  if (cached) return cached
  const index = buildNameIndex(catalog)
  const ranked = new Map(catalog.map((s) => [s.slug, rankRelated(s, catalog, index)]))
  const inbound = new Map(catalog.map((s) => [s.slug, 0]))
  const out = new Map<string, CatalogStrain[]>()
  for (const s of catalog) {
    const picks = ranked.get(s.slug)!.slice(0, RELEVANCE_SLOTS)
    for (const p of picks) inbound.set(p.slug, inbound.get(p.slug)! + 1)
    out.set(s.slug, picks)
  }
  for (const s of catalog) {
    const picks = out.get(s.slug)!
    const pool = ranked.get(s.slug)!.slice(RELEVANCE_SLOTS, DISCOVERY_POOL)
    while (picks.length < RELATED_STRAIN_COUNT && pool.length) {
      // least-linked first; pool order (relevance) breaks ties
      let best = 0
      for (let i = 1; i < pool.length; i++) if (inbound.get(pool[i].slug)! < inbound.get(pool[best].slug)!) best = i
      const [p] = pool.splice(best, 1)
      picks.push(p)
      inbound.set(p.slug, inbound.get(p.slug)! + 1)
    }
  }
  relatedMemo.set(catalog, out)
  return out
}

export function getRelatedStrains(target: CatalogStrain, catalog: CatalogStrain[]): CatalogStrain[] {
  return getRelatedStrainsMap(catalog).get(target.slug) ?? []
}
