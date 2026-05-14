import { Suspense } from 'react'
import { getSortedPostsData } from '@/lib/posts'
import ArticlesTabs from '@/components/ArticlesTabs'
import type { Metadata } from 'next'

export const revalidate = 3600 // Revalidate every hour

const baseUrl = 'https://thegreenleaf.com'

export const metadata: Metadata = {
  title: 'Cannabis Articles & Guides - Expert Tips for Every Season',
  description: 'Browse expert cannabis articles and guides. Find advice on growing, strains, nutrients, harvesting, and wellness for every experience level.',
  openGraph: {
    title: 'All Cannabis Articles & Guides',
    description: 'Browse our complete library of cannabis articles, guides, and expert tips for a healthier, greener cannabis.',
    url: `${baseUrl}/articles`,
    siteName: 'The Green Leaf',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-articles.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Green Leaf - Expert Cannabis Articles',
    }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'All Cannabis Articles & Guides',
    description: 'Browse our complete library of cannabis articles and expert tips.',
    images: [`${baseUrl}/images/og-articles.jpg`],
  },
  alternates: {
    canonical: `${baseUrl}/articles`,
  },
}

export default function ArticlesPage() {
  const allPosts = getSortedPostsData()

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-serif text-gray-900 mb-8">
          Cannabis Articles & Guides
        </h1>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Expert cannabis advice for every season. From spring preparation to winter protection,
          find professional tips for a healthier, greener cannabis.
        </p>
      </div>

      {allPosts.length === 0 ? (
        <div className="bg-leaf-50 rounded-lg p-8 text-center">
          <p className="text-leaf-700 text-lg mb-4">
            No articles published yet.
          </p>
          <div className="text-left max-w-xl mx-auto bg-white p-6 rounded shadow-sm">
            <h3 className="font-semibold mb-3">To add articles:</h3>
            <ol className="list-decimal pl-5 space-y-2 text-sm text-gray-700">
              <li>Run the content generator to create drafts</li>
              <li>Review drafts in the <code className="bg-gray-100 px-1">drafts/</code> folder</li>
              <li>Move approved articles to <code className="bg-gray-100 px-1">content/posts/</code></li>
              <li>Commit and push to redeploy</li>
            </ol>
          </div>
        </div>
      ) : (
        <Suspense fallback={
          <div>
            <div className="flex flex-wrap justify-center gap-2 mb-8">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-10 w-20 bg-gray-200 rounded-full animate-pulse" />
              ))}
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-md overflow-hidden">
                  <div className="md:flex">
                    <div className="md:w-64 md:flex-shrink-0">
                      <div className="h-48 bg-gray-200 animate-pulse" />
                    </div>
                    <div className="p-6 flex-1 space-y-3">
                      <div className="flex gap-2">
                        <div className="h-5 w-16 bg-gray-200 rounded-full animate-pulse" />
                        <div className="h-5 w-20 bg-gray-200 rounded animate-pulse" />
                      </div>
                      <div className="h-6 w-3/4 bg-gray-200 rounded animate-pulse" />
                      <div className="h-4 w-full bg-gray-200 rounded animate-pulse" />
                      <div className="h-4 w-2/3 bg-gray-200 rounded animate-pulse" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        }>
          <ArticlesTabs posts={allPosts} />
        </Suspense>
      )}
    </div>
  )
}
