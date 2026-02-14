'use client'

import Link from 'next/link'

export default function SearchError({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="max-w-2xl mx-auto px-4 py-24 text-center">
      <h2 className="text-2xl font-bold text-grass-900 mb-4">
        Search unavailable
      </h2>
      <p className="text-gray-600 mb-8">
        We had trouble processing your search. Please try again.
      </p>
      <div className="flex gap-4 justify-center">
        <button
          onClick={reset}
          className="px-6 py-3 bg-grass-600 text-white rounded-full font-medium hover:bg-grass-700 transition-colors"
        >
          Try Again
        </button>
        <Link
          href="/articles"
          className="px-6 py-3 border border-grass-600 text-grass-600 rounded-full font-medium hover:bg-grass-50 transition-colors"
        >
          Browse Articles
        </Link>
      </div>
    </div>
  )
}
