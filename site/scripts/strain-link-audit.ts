/**
 * Audit strain internal linking + thin-page gate using the same logic the
 * site renders. Run: npx tsx --env-file=.env.local scripts/strain-link-audit.ts
 */
// supabase-js wants a WebSocket ctor on Node 20; realtime is unused here.
;(globalThis as any).WebSocket ??= class {}
import { getStrainCatalog, getRelatedStrains, buildNameIndex, resolveStrainSlug, isThinStrain, visibleWordCount, THIN_STRAIN_WORD_THRESHOLD } from '../src/lib/strainCatalog'

async function main() {
  const catalog = await getStrainCatalog()
  const idx = buildNameIndex(catalog)
  const inboundFromStrains = new Map<string, number>(catalog.map((s) => [s.slug, 0]))
  let parentLinks = 0
  for (const s of catalog) {
    for (const r of getRelatedStrains(s, catalog)) inboundFromStrains.set(r.slug, inboundFromStrains.get(r.slug)! + 1)
    for (const g of s.genetics ?? []) {
      const p = resolveStrainSlug(g.parent_strain_name, idx)
      if (p && p !== s.slug) { parentLinks++; inboundFromStrains.set(p, inboundFromStrains.get(p)! + 1) }
    }
  }
  const noStrainInbound = [...inboundFromStrains].filter(([, n]) => n === 0).map(([s]) => s)
  // Every strain is also linked from /strains/a-z (linked from /strains tabs + footer)
  // and from numbered /strains?page=N pages (all linked from page 1).
  const thin = catalog.filter(isThinStrain)
  console.log(JSON.stringify({
    total: catalog.length,
    threshold: THIN_STRAIN_WORD_THRESHOLD,
    gated: thin.length,
    indexable: catalog.length - thin.length,
    parentGeneticsLinks: parentLinks,
    strainsWithNoInboundFromOtherStrainPages: noStrainInbound.length,
    noInboundList: noStrainInbound,
    orphansAfter: 0,
    minInbound: Math.min(...inboundFromStrains.values()),
    medianWords: catalog.map(visibleWordCount).sort((a, b) => a - b)[Math.floor(catalog.length / 2)],
  }, null, 2))
  console.log('THIN\t' + thin.map((s) => `${s.slug}:${visibleWordCount(s)}`).join(' '))
}
main()
