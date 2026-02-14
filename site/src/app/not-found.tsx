import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-24 text-center">
      <h1 className="text-6xl font-bold text-grass-300 mb-4">404</h1>
      <h2 className="text-2xl font-bold text-grass-900 mb-4">
        Page not found
      </h2>
      <p className="text-gray-600 mb-8">
        The page you&apos;re looking for doesn&apos;t exist or may have been moved.
      </p>
      <div className="flex flex-wrap gap-4 justify-center">
        <Link
          href="/"
          className="px-6 py-3 bg-grass-600 text-white rounded-full font-medium hover:bg-grass-700 transition-colors"
        >
          Go Home
        </Link>
        <Link
          href="/articles"
          className="px-6 py-3 border border-grass-600 text-grass-600 rounded-full font-medium hover:bg-grass-50 transition-colors"
        >
          Browse Articles
        </Link>
        <Link
          href="/topics"
          className="px-6 py-3 border border-grass-600 text-grass-600 rounded-full font-medium hover:bg-grass-50 transition-colors"
        >
          View Topics
        </Link>
      </div>
    </div>
  )
}
