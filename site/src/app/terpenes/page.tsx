import { getSupabase } from '@/lib/supabase'
import Link from 'next/link'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import { TERPENES, TERPENE_SLUGS } from '@/lib/terpenes'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Cannabis Terpenes Guide | The Strain Report',
  description:
    'Learn about the major cannabis terpenes — myrcene, caryophyllene, limonene, linalool, pinene, and terpinolene. Effects, aromas, and the strains highest in each.',
  openGraph: {
    title: 'Cannabis Terpenes Guide | The Strain Report',
    description:
      'Effects, aromas, and the strains highest in every major cannabis terpene.',
    url: `${baseUrl}/terpenes`,
    siteName: 'The Strain Report',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cannabis Terpenes Guide | The Strain Report',
    description:
      'Effects, aromas, and the strains highest in every major cannabis terpene.',
  },
  alternates: { canonical: `${baseUrl}/terpenes` },
}

export default async function TerpenesIndexPage() {
  // One query for all six terpenes, then group in JS
  let counts: Record<string, number> = {}
  try {
    const { data } = await getSupabase()
      .from('terpenes')
      .select('terpene_name, strains!inner(published)')
      .in('terpene_name', TERPENE_SLUGS)
      .eq('strains.published', true)
    const rows = (data as { terpene_name: string }[] | null) ?? []
    counts = rows.reduce<Record<string, number>>((acc, r) => {
      acc[r.terpene_name] = (acc[r.terpene_name] ?? 0) + 1
      return acc
    }, {})
  } catch {
    // env unavailable during build
  }

  // Cards sorted by count desc
  const cards = TERPENE_SLUGS
    .map((slug) => ({ ...TERPENES[slug], count: counts[slug] ?? 0 }))
    .sort((a, b) => b.count - a.count)

  // BreadcrumbList: Home → Terpenes
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home',     item: baseUrl },
      { '@type': 'ListItem', position: 2, name: 'Terpenes', item: `${baseUrl}/terpenes` },
    ],
  }

  return (
    <div className="bg-[#f0f0f0]">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />

      {/* Top separator */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* Hero */}
      <div className="relative py-16 overflow-hidden">
        <BlinkingSquares
          className="absolute inset-0"
          width="100%"
          height="100%"
          direction="right"
          gridSize={52}
          squareColor="#14B8A6"
          backgroundColor="#f0f0f0"
          falloff={1.25}
          fadeStart={0.33}
          fadeEnd={1}
          squareSize={0.57}
          minBrightness={0.55}
          twinkleSpeed={1.4}
          twinkleStrength={0.94}
          intensity={1}
          opacity={0.4}
          dpr={1.5}
        />
        <div className="relative z-10 max-w-6xl mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#1a3a0a' }}>
            Cannabis Terpenes Guide
          </h1>
          <p className="text-xl max-w-2xl" style={{ color: '#2d4a1e' }}>
            Terpenes are the aromatic compounds that give each cannabis strain its unique smell, taste, and effect profile. Explore the six most influential terpenes.
          </p>
        </div>
      </div>

      {/* Bottom separator */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* Cards grid */}
      <div className="px-4 sm:px-6 md:px-[160px] py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {cards.map((c) => (
            <Link
              key={c.slug}
              href={`/terpenes/${c.slug}`}
              className="bg-white rounded-xl border border-gray-200 p-6 flex flex-col gap-3 hover:border-[#2D5016]/30 hover:shadow-sm transition-all no-underline"
            >
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-serif text-2xl text-gray-900 leading-tight">{c.displayName}</h2>
                <span className="shrink-0 text-xs font-medium bg-emerald-100 text-emerald-700 px-2.5 py-1 rounded-full">
                  {c.count} {c.count === 1 ? 'strain' : 'strains'}
                </span>
              </div>
              <p className="text-sm text-gray-600 line-clamp-3 leading-relaxed">{c.shortDescription}</p>
              <span className="mt-auto pt-2 text-sm font-medium text-[#2D5016] inline-flex items-center gap-1">
                Explore {c.displayName} <span aria-hidden="true">→</span>
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
