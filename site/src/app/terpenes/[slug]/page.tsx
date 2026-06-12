import { getSupabase } from '@/lib/supabase'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import StrainCard from '@/components/StrainCard'
import { getTerpene } from '@/lib/terpenes'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

type StrainRow = {
  percentage: number | null
  strains: {
    slug: string
    name: string
    strain_type: 'indica' | 'sativa' | 'hybrid'
    thc_min: number | null
    thc_max: number | null
    short_description: string | null
    flavors: string[] | null
  }
}

// ── Metadata ───────────────────────────────────────────────────────────────

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const terpene = getTerpene(slug)
  if (!terpene) return {}
  return {
    title: terpene.seoTitle,
    description: terpene.seoDescription,
    openGraph: {
      title: terpene.seoTitle,
      description: terpene.seoDescription,
      url: `${baseUrl}/terpenes/${slug}`,
      siteName: 'The Strain Report',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: terpene.seoTitle,
      description: terpene.seoDescription,
    },
    alternates: { canonical: `${baseUrl}/terpenes/${slug}` },
  }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function TerpeneHubPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const terpene = getTerpene(slug)
  if (!terpene) notFound()

  // Fetch all strains containing this terpene, ordered by percentage desc
  let rows: StrainRow[] = []
  try {
    const { data } = await getSupabase()
      .from('terpenes')
      .select('percentage, strains!inner(slug, name, strain_type, thc_min, thc_max, short_description, flavors, published)')
      .eq('terpene_name', terpene.displayName)
      .eq('strains.published', true)
      .order('percentage', { ascending: false })
    rows = (data as unknown as StrainRow[]) ?? []
  } catch {
    // env unavailable during build
  }

  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home',                  item: baseUrl },
      { '@type': 'ListItem', position: 2, name: 'Terpenes',              item: `${baseUrl}/terpenes` },
      { '@type': 'ListItem', position: 3, name: terpene.displayName,     item: `${baseUrl}/terpenes/${slug}` },
    ],
  }

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: terpene.faqs.map((f) => ({
      '@type': 'Question',
      name: f.question,
      acceptedAnswer: { '@type': 'Answer', text: f.answer },
    })),
  }

  return (
    <div className="bg-[#f0f0f0]">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

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
          {/* Breadcrumb */}
          <nav className="text-sm mb-4" aria-label="Breadcrumb" style={{ color: '#2d4a1e' }}>
            <ol className="flex flex-wrap items-center gap-1.5">
              <li><Link href="/" className="hover:text-leaf-700 no-underline" style={{ color: 'inherit' }}>Home</Link></li>
              <li aria-hidden="true">/</li>
              <li><Link href="/terpenes" className="hover:text-leaf-700 no-underline" style={{ color: 'inherit' }}>Terpenes</Link></li>
              <li aria-hidden="true">/</li>
              <li><span className="font-medium">{terpene.displayName}</span></li>
            </ol>
          </nav>

          <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#1a3a0a' }}>
            {terpene.displayName}
          </h1>
          <p className="text-lg max-w-3xl mb-4 leading-relaxed" style={{ color: '#2d4a1e' }}>
            {terpene.shortDescription}
          </p>
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/70 backdrop-blur-sm text-sm font-medium border border-emerald-300/40" style={{ color: '#2d4a1e' }}>
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Found in {rows.length} {rows.length === 1 ? 'strain' : 'strains'}
          </span>
        </div>
      </div>

      {/* Bottom separator */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      <div className="px-4 sm:px-6 md:px-[160px] py-12">
        {/* Strain grid */}
        {rows.length === 0 ? (
          <p className="text-gray-500 text-center py-16">
            No published strains currently list {terpene.displayName} in their profile.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {rows.map((r, i) => (
              <StrainCard
                key={`${r.strains.slug}-${i}`}
                strain={{
                  id: r.strains.slug,
                  name: r.strains.name,
                  slug: r.strains.slug,
                  strain_type: r.strains.strain_type,
                  thc_min: r.strains.thc_min,
                  thc_max: r.strains.thc_max,
                  short_description: r.strains.short_description,
                  flavors: r.strains.flavors,
                }}
                terpenePercentage={r.percentage ?? undefined}
              />
            ))}
          </div>
        )}

        {/* FAQs */}
        <section className="mt-16">
          <h2 className="font-serif text-2xl text-gray-900 mb-6">Frequently asked questions about {terpene.displayName}</h2>
          <div className="flex flex-col gap-3">
            {terpene.faqs.map((f, i) => (
              <details
                key={i}
                className="bg-white rounded-xl border border-gray-200 px-5 py-4 group"
              >
                <summary className="cursor-pointer font-medium text-gray-900 list-none flex items-center justify-between gap-3">
                  {f.question}
                  <span className="text-gray-400 text-sm transition-transform group-open:rotate-45" aria-hidden="true">+</span>
                </summary>
                <p className="mt-3 text-gray-600 leading-relaxed">{f.answer}</p>
              </details>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
