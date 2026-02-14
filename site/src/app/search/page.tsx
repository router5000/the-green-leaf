import Link from 'next/link'
import type { Metadata } from 'next'
import { getSortedPostsData } from '@/lib/posts'
import { search } from '@/lib/search'
import SearchResults from '@/components/SearchResults'

interface SearchPageProps {
  searchParams: Promise<{ q?: string }>
}

export async function generateMetadata({ searchParams }: SearchPageProps): Promise<Metadata> {
  const params = await searchParams
  const query = params.q || ''

  return {
    title: query ? `Search: ${query} - Lawn Care Center` : 'Search - Lawn Care Center',
    description: query
      ? `Search results for "${query}" - Find lawn care articles and videos`
      : 'Search lawn care articles and videos',
    robots: {
      index: false,
      follow: true,
    },
  }
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const params = await searchParams
  const query = params.q || ''
  const allPosts = getSortedPostsData()

  const results = query ? search(allPosts, query) : { articles: [], videos: [], totalCount: 0 }

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      {/* Search Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-grass-900 mb-4">
          {query ? (
            <>
              Search Results for{' '}
              <span className="text-grass-600">&ldquo;{query}&rdquo;</span>
            </>
          ) : (
            'Search'
          )}
        </h1>
        {query && results.totalCount > 0 && (
          <p className="text-gray-600">
            Found {results.totalCount} result{results.totalCount !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {/* No Query State */}
      {!query && (
        <div className="bg-grass-50 rounded-xl p-12 text-center">
          <svg
            className="w-16 h-16 mx-auto text-grass-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-grass-900 mb-2">
            Search Our Library
          </h2>
          <p className="text-gray-600 mb-6">
            Find lawn care articles, tips, and expert video guides
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            <span className="text-sm text-gray-500">Popular searches:</span>
            {['aeration', 'fertilizer', 'weed control', 'mowing', 'overseeding'].map((term) => (
              <Link
                key={term}
                href={`/search?q=${encodeURIComponent(term)}`}
                className="px-3 py-1 bg-white text-grass-700 rounded-full text-sm hover:bg-grass-100 transition border border-grass-200"
              >
                {term}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* No Results State */}
      {query && results.totalCount === 0 && (
        <div className="bg-gray-50 rounded-xl p-12 text-center">
          <svg
            className="w-16 h-16 mx-auto text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No results found
          </h2>
          <p className="text-gray-600 mb-6">
            We couldn&apos;t find anything matching &ldquo;{query}&rdquo;
          </p>
          <div className="space-y-4">
            <p className="text-sm text-gray-500">Try:</p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Using different keywords</li>
              <li>• Checking your spelling</li>
              <li>• Using more general terms</li>
            </ul>
            <Link
              href="/articles"
              className="inline-block mt-4 px-6 py-2 bg-grass-600 text-white rounded-lg hover:bg-grass-700 transition"
            >
              Browse All Articles
            </Link>
          </div>
        </div>
      )}

      {/* Search Results with Tabs */}
      {query && results.totalCount > 0 && (
        <SearchResults
          articles={results.articles}
          videos={results.videos}
          query={query}
        />
      )}

      {/* Back to Articles Link */}
      {query && results.totalCount > 0 && (
        <div className="mt-12 text-center">
          <Link
            href="/articles"
            className="text-grass-600 hover:text-grass-800 font-medium"
          >
            ← Browse All Articles
          </Link>
        </div>
      )}
    </div>
  )
}
