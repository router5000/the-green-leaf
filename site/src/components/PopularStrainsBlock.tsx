import Link from 'next/link'
import type { CatalogStrain } from '@/lib/strainCatalog'

const TYPE_BADGE: Record<string, string> = {
  indica: 'bg-purple-100 text-purple-700',
  sativa: 'bg-green-100 text-green-700',
  hybrid: 'bg-orange-100 text-orange-600',
}

/**
 * Server-rendered block of crawlable <a href> links to popular strain
 * profiles plus the /strains and /states hubs. Used on the homepage, the
 * /strains hub and strain profiles to spread internal links to top strains.
 */
export default function PopularStrainsBlock({
  strains,
  title = 'Popular strains',
  headingId = 'popular-strains-heading',
  showHubLinks = true,
  className = '',
}: {
  strains: CatalogStrain[]
  title?: string
  headingId?: string
  showHubLinks?: boolean
  className?: string
}) {
  if (!strains.length && !showHubLinks) return null
  return (
    <section className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`} aria-labelledby={headingId}>
      <h2 id={headingId} className="font-serif text-xl text-gray-900 mb-4">{title}</h2>
      {strains.length > 0 && (
        <ul className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {strains.map((s) => (
            <li key={s.slug}>
              <Link
                href={`/strains/${s.slug}`}
                className="flex items-center justify-between gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm hover:border-leaf-300 no-underline transition-colors"
              >
                <span className="text-gray-800 font-medium">{s.name}</span>
                <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full capitalize ${TYPE_BADGE[s.strain_type] ?? 'bg-gray-100 text-gray-600'}`}>
                  {s.strain_type}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      {showHubLinks && (
        <p className="mt-4 text-sm flex flex-wrap gap-x-4 gap-y-1">
          <Link href="/strains" className="text-leaf-700 hover:text-leaf-800">Browse all strains →</Link>
          <Link href="/strains/a-z" className="text-leaf-700 hover:text-leaf-800">Strains A–Z →</Link>
          <Link href="/strains/compare" className="text-leaf-700 hover:text-leaf-800">Compare strains →</Link>
          <Link href="/states" className="text-leaf-700 hover:text-leaf-800">Cannabis laws by state →</Link>
        </p>
      )}
    </section>
  )
}
