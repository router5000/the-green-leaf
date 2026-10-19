import Link from 'next/link'
import type { Metadata } from 'next'
import { getStrainCatalogSafe } from '@/lib/strainCatalog'

export const revalidate = 86400

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'All Cannabis Strains A–Z | The Strain Report',
  description: 'Alphabetical index of every cannabis strain profile on The Strain Report — indica, sativa, and hybrid strains with effects, terpenes, and genetics.',
  alternates: { canonical: `${baseUrl}/strains/a-z` },
  openGraph: {
    title: 'All Cannabis Strains A–Z | The Strain Report',
    url: `${baseUrl}/strains/a-z`,
    siteName: 'The Strain Report',
    type: 'website',
  },
}

function letterOf(name: string): string {
  const c = name.trim().charAt(0).toUpperCase()
  return /[A-Z]/.test(c) ? c : '#'
}

export default async function StrainsAZPage() {
  const catalog = await getStrainCatalogSafe()
  const groups = new Map<string, { name: string; slug: string; strain_type: string }[]>()
  for (const s of [...catalog].sort((a, b) => a.name.localeCompare(b.name))) {
    const l = letterOf(s.name)
    if (!groups.has(l)) groups.set(l, [])
    groups.get(l)!.push(s)
  }
  const letters = [...groups.keys()].sort((a, b) => (a === '#' ? -1 : b === '#' ? 1 : a.localeCompare(b)))

  return (
    <div className="min-h-screen bg-[#f0f0f0] px-4 sm:px-6 md:px-[160px] pt-10 pb-16">
      <nav className="text-sm text-gray-500 mb-6" aria-label="Breadcrumb">
        <Link href="/" className="hover:text-leaf-700 no-underline">Home</Link>
        <span className="mx-1.5">/</span>
        <Link href="/strains" className="hover:text-leaf-700 no-underline">Strains</Link>
        <span className="mx-1.5">/</span>
        <span className="text-gray-700 font-medium">A–Z</span>
      </nav>
      <h1 className="font-serif text-4xl md:text-5xl text-gray-900 mb-3">All Strains A–Z</h1>
      <p className="text-gray-600 mb-8">{catalog.length} strain profiles, alphabetically.</p>

      <nav className="flex flex-wrap gap-2 mb-10" aria-label="Jump to letter">
        {letters.map((l) => (
          <a key={l} href={`#letter-${l === '#' ? 'num' : l}`} className="w-9 h-9 flex items-center justify-center rounded-full bg-white border border-gray-200 text-sm font-medium text-gray-700 hover:border-leaf-300 no-underline">
            {l}
          </a>
        ))}
      </nav>

      <div className="flex flex-col gap-10">
        {letters.map((l) => (
          <section key={l} id={`letter-${l === '#' ? 'num' : l}`}>
            <h2 className="font-serif text-2xl text-gray-900 mb-3">{l}</h2>
            <ul className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-2">
              {groups.get(l)!.map((s) => (
                <li key={s.slug}>
                  <Link href={`/strains/${s.slug}`} className="text-sm text-leaf-700 hover:text-leaf-800">
                    {s.name}
                  </Link>
                  <span className="ml-1.5 text-xs text-gray-400 capitalize">{s.strain_type}</span>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  )
}
