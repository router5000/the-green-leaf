import { getSortedPostsData } from '@/lib/posts'
import { getStrainCatalogSafe, isThinStrain } from '@/lib/strainCatalog'
import { statesData } from '@/data/statesData'

export const revalidate = 86400
const BASE = 'https://strainreport.com'

export async function GET() {
  const posts = getSortedPostsData()
  const strains = (await getStrainCatalogSafe()).filter(s => !isThinStrain(s))
  const lines: string[] = [
    '# The Strain Report — full content index',
    '',
    '> Complete list of articles, strain profiles, and state cannabis-law guides on strainreport.com. Append `.md` to any page URL (or send `Accept: text/markdown`) to get a clean Markdown version.',
    '',
    `## Articles (${posts.length})`, '',
    ...posts.map(p => `- [${p.title}](${BASE}/articles/${p.slug}): ${p.meta_description || ''}`.trim()),
    '', `## Strain profiles (${strains.length})`, '',
    ...strains.map(s => `- [${s.name}](${BASE}/strains/${s.slug}) (${s.strain_type}): ${(s.short_description || '').replace(/\s+/g, ' ')}`.trim()),
    '', '## State cannabis laws (50)', '',
    ...statesData.map(s => `- [${s.name}](${BASE}/states/${s.slug}): ${s.legalStatus}; possession: ${s.possessionLimit}; home grow: ${s.homeGrow}`),
    '',
  ]
  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'public, s-maxage=86400' },
  })
}
