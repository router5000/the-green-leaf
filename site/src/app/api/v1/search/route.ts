import { getSortedPostsData } from '@/lib/posts'
import { getStrainCatalogSafe } from '@/lib/strainCatalog'
import { statesData } from '@/data/statesData'

export const revalidate = 3600
const BASE = 'https://strainreport.com'

/** Read-only public lookup across strains, articles, and state law pages. */
export async function GET(req: Request) {
  const url = new URL(req.url)
  const q = (url.searchParams.get('q') || '').trim().toLowerCase().slice(0, 100)
  const type = url.searchParams.get('type') || 'all'
  const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') || '10', 10) || 10, 1), 50)
  if (!q) {
    return Response.json({ error: 'Missing q parameter', example: `${BASE}/api/v1/search?q=blue+dream` }, { status: 400 })
  }
  const out: Record<string, unknown[]> = {}
  if (type === 'all' || type === 'strain') {
    const catalog = await getStrainCatalogSafe()
    out.strains = catalog
      .filter(s => s.name.toLowerCase().includes(q) || (s.aka || []).some(a => a.toLowerCase().includes(q)))
      .slice(0, limit)
      .map(s => ({
        name: s.name, slug: s.slug, type: s.strain_type,
        summary: s.short_description,
        effects: (s.effects || []).map(e => e.effect_name),
        terpenes: (s.terpenes || []).map(t => t.terpene_name),
        flavors: s.flavors,
        parents: (s.genetics || []).map(g => g.parent_strain_name),
        url: `${BASE}/strains/${s.slug}`, markdown: `${BASE}/strains/${s.slug}.md`,
      }))
  }
  if (type === 'all' || type === 'article') {
    out.articles = getSortedPostsData()
      .filter(p => p.title.toLowerCase().includes(q) || (p.keyword || '').toLowerCase().includes(q) || (p.tags || []).some(t => t.toLowerCase().includes(q)))
      .slice(0, limit)
      .map(p => ({ title: p.title, slug: p.slug, summary: p.meta_description, tags: p.tags, url: `${BASE}/articles/${p.slug}`, markdown: `${BASE}/articles/${p.slug}.md` }))
  }
  if (type === 'all' || type === 'state') {
    out.states = statesData
      .filter(s => s.name.toLowerCase().includes(q) || s.slug.includes(q))
      .slice(0, limit)
      .map(s => ({ name: s.name, slug: s.slug, legalStatus: s.legalStatus, possessionLimit: s.possessionLimit, homeGrow: s.homeGrow, minimumAge: s.purchaseAge, officialSource: s.officialLink, url: `${BASE}/states/${s.slug}`, note: 'General information, not legal advice. Laws change; verify with the official source.' }))
  }
  return Response.json({ query: q, results: out, source: 'The Strain Report (strainreport.com)' }, {
    headers: { 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400' },
  })
}
