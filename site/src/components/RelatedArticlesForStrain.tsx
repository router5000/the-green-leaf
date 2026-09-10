import Link from 'next/link'

type RelatedArticle = {
  slug: string
  title: string
  meta_description?: string
}

export default function RelatedArticlesForStrain({
  strainName,
  articles,
}: {
  strainName: string
  articles: RelatedArticle[]
}) {
  if (articles.length === 0) return null

  return (
    <section
      className="bg-white rounded-xl border border-gray-200 p-6"
      aria-label={`Guides and reviews for ${strainName}`}
    >
      <h2 className="font-serif text-xl text-gray-900 mb-2">Full guides &amp; reviews</h2>
      <p className="text-sm text-gray-500 mb-4">
        In-depth editorial coverage of {strainName} on The Strain Report.
      </p>
      <ul className="flex flex-col gap-3">
        {articles.map((article) => (
          <li key={article.slug}>
            <Link
              href={`/articles/${article.slug}`}
              className="block rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 hover:border-leaf-300 hover:bg-leaf-50 transition no-underline"
            >
              <span className="font-medium text-leaf-800">{article.title}</span>
              {article.meta_description && (
                <span className="block text-sm text-gray-500 mt-1 line-clamp-2">
                  {article.meta_description}
                </span>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
