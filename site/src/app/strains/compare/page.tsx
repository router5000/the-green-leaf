import { getSupabase } from '@/lib/supabase'
import Link from 'next/link'
import CompareAnotherStrain from '@/components/CompareAnotherStrain'
import { COMPARISON_PAIRS } from '@/data/strainComparisonPairs'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Cannabis Strain Comparison Tool | The Strain Report',
  description: 'Compare cannabis strains side by side. See THC, CBD, effects, terpenes, flowering time, yields, and growing difficulty for any two strains in our database.',
  openGraph: {
    title: 'Cannabis Strain Comparison Tool | The Strain Report',
    description: 'Compare any two cannabis strains side by side — THC, CBD, effects, terpenes, growing info, and more.',
    url: `${baseUrl}/strains/compare`,
    siteName: 'The Strain Report',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cannabis Strain Comparison Tool',
    description: 'Compare any two cannabis strains side by side.',
  },
  alternates: { canonical: `${baseUrl}/strains/compare` },
}

export default async function CompareLandingPage() {
  let allSlugs: { slug: string; name: string; strain_type: string }[] = []
  try {
    const { data } = await getSupabase()
      .from('strains')
      .select('slug, name, strain_type')
      .eq('published', true)
      .order('name')
    allSlugs = (data as typeof allSlugs) ?? []
  } catch {
    // env unavailable
  }

  const lookup = new Map(allSlugs.map((s) => [s.slug, s]))
  const popularPairs = COMPARISON_PAIRS.map(([a, b]) => ({
    slugA: a,
    slugB: b,
    nameA: lookup.get(a)?.name ?? a,
    nameB: lookup.get(b)?.name ?? b,
    typeA: lookup.get(a)?.strain_type ?? null,
    typeB: lookup.get(b)?.strain_type ?? null,
  }))

  const TYPE_BADGE: Record<string, string> = {
    indica: 'bg-purple-100 text-purple-700',
    sativa: 'bg-green-100 text-green-700',
    hybrid: 'bg-orange-100 text-orange-600',
  }

  return (
    <div className="min-h-screen bg-[#f0f0f0]">
      <div className="px-4 sm:px-6 md:px-[160px] pt-10 pb-16">
        {/* Breadcrumb */}
        <nav className="text-sm text-gray-500 mb-6" aria-label="Breadcrumb">
          <ol className="flex flex-wrap items-center gap-1.5">
            <li><Link href="/" className="hover:text-leaf-700 no-underline">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/strains" className="hover:text-leaf-700 no-underline">Strains</Link></li>
            <li aria-hidden="true">/</li>
            <li><span className="text-gray-700 font-medium">Compare</span></li>
          </ol>
        </nav>

        <h1 className="font-serif text-4xl md:text-5xl text-gray-900 mb-3">
          Cannabis Strain Comparison Tool
        </h1>
        <p className="text-lg text-gray-600 leading-relaxed mb-10 max-w-3xl">
          Compare any two cannabis strains side by side. See how they differ in THC and CBD content,
          effects, terpene profile, flowering time, yields, and growing difficulty. Pick two strains
          below or jump into one of our popular comparisons.
        </p>

        {/* Compare form */}
        <CompareAnotherStrain slugs={allSlugs.map(({ slug, name }) => ({ slug, name }))} />

        {/* Popular comparisons */}
        <div className="mt-16">
          <h2 className="font-serif text-2xl text-gray-900 mb-6">Popular Comparisons</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {popularPairs.map((p) => (
              <Link
                key={`${p.slugA}-vs-${p.slugB}`}
                href={`/strains/compare/${p.slugA}-vs-${p.slugB}`}
                className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3 hover:border-[#2D5016]/30 hover:shadow-sm transition-all no-underline"
              >
                <p className="text-base font-medium text-gray-900">
                  {p.nameA} <span className="text-gray-400">vs</span> {p.nameB}
                </p>
                <div className="flex gap-2">
                  {p.typeA && (
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${TYPE_BADGE[p.typeA] ?? 'bg-gray-100 text-gray-600'}`}>
                      {p.typeA}
                    </span>
                  )}
                  {p.typeB && (
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${TYPE_BADGE[p.typeB] ?? 'bg-gray-100 text-gray-600'}`}>
                      {p.typeB}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
