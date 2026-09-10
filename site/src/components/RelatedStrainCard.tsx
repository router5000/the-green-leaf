import Link from 'next/link'
import type { ArticleStrainLink } from '@/lib/strainArticleLinks'
import { TERPENES } from '@/lib/terpenes'

export default function RelatedStrainCard({ link }: { link: ArticleStrainLink }) {
  return (
    <aside
      className="my-10 rounded-xl border border-leaf-200 bg-leaf-50 p-6"
      aria-label={`Strain profile for ${link.strainName}`}
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-leaf-600 mb-2">
        Strain profile
      </p>
      <h2 className="text-xl font-semibold text-leaf-900 mb-2">
        <Link
          href={`/strains/${link.strainSlug}`}
          className="hover:text-leaf-600 transition"
        >
          {link.strainName} strain database page
        </Link>
      </h2>
      <p className="text-gray-600 mb-4 text-sm leading-relaxed">
        Effects, terpenes, genetics, and growing notes for{' '}
        <Link
          href={`/strains/${link.strainSlug}`}
          className="text-leaf-700 font-medium hover:underline"
        >
          {link.strainName}
        </Link>
        .
      </p>

      {link.terpeneSlugs.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-leaf-600 mb-2">
            Related terpenes
          </p>
          <ul className="flex flex-wrap gap-2">
            {link.terpeneSlugs.map((slug) => {
              const entry = TERPENES[slug]
              const label = entry?.displayName ?? slug
              return (
                <li key={slug}>
                  <Link
                    href={`/terpenes/${slug}`}
                    className="inline-flex items-center rounded-full bg-white border border-leaf-200 px-3 py-1 text-sm text-leaf-800 hover:border-leaf-400 hover:text-leaf-600 transition"
                  >
                    {label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </aside>
  )
}
