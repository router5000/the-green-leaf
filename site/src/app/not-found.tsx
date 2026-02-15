import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-24 text-center">
      <h1 className="text-6xl font-bold text-leaf-300 mb-4">404</h1>
      <h2 className="text-2xl font-bold text-leaf-900 mb-4">
        Page not found
      </h2>
      <p className="text-gray-600 mb-8">
        The page you&apos;re looking for doesn&apos;t exist or may have been moved.
      </p>
      <div className="flex flex-wrap gap-4 justify-center">
        <Link
          href="/"
          className="px-6 py-3 bg-leaf-600 text-white rounded-full font-medium hover:bg-leaf-700 transition-colors"
        >
          Go Home
        </Link>
        <Link
          href="/articles"
          className="px-6 py-3 border border-leaf-600 text-leaf-600 rounded-full font-medium hover:bg-leaf-50 transition-colors"
        >
          Browse Articles
        </Link>
        <Link
          href="/topics"
          className="px-6 py-3 border border-leaf-600 text-leaf-600 rounded-full font-medium hover:bg-leaf-50 transition-colors"
        >
          View Topics
        </Link>
      </div>
    </div>
  )
}
