'use client'

import Link from 'next/link'

export default function TopicsError({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="max-w-2xl mx-auto px-4 py-24 text-center">
      <h2 className="text-2xl font-bold text-leaf-900 mb-4">
        Unable to load topics
      </h2>
      <p className="text-gray-600 mb-8">
        We had trouble loading the topics page. Please try again.
      </p>
      <div className="flex gap-4 justify-center">
        <button
          onClick={reset}
          className="px-6 py-3 bg-leaf-600 text-white rounded-full font-medium hover:bg-leaf-700 transition-colors"
        >
          Try Again
        </button>
        <Link
          href="/"
          className="px-6 py-3 border border-leaf-600 text-leaf-600 rounded-full font-medium hover:bg-leaf-50 transition-colors"
        >
          Go Home
        </Link>
      </div>
    </div>
  )
}
