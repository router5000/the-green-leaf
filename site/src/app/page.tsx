import Link from 'next/link'
import { getSortedPostsData, getMonthlyPosts } from '@/lib/posts'
import HomeContent from '@/components/HomeContent'
import BlinkingSquares from '@/components/react-bits/blinking-squares'

export default function Home() {
  const allPosts = getSortedPostsData()
  const featuredPost = allPosts[0]
  const { posts: monthlyPosts, monthName } = getMonthlyPosts(3)
  const bottomPosts = allPosts.slice(4, 6)

  return (
    <div className="bg-white min-h-screen">

      {/* ── Full-viewport hero ──────────────────────────────────────────── */}
      <section className="min-h-screen flex flex-col md:flex-row overflow-hidden">

        {/* Right column (desktop) / top banner (mobile) — BlinkingSquares only */}
        {/* order-first on mobile puts it at top; md:order-last shifts it right on desktop */}
        <div className="h-56 sm:h-72 md:h-auto md:w-1/2 relative order-first md:order-last flex-shrink-0">
          <BlinkingSquares
            className="absolute inset-0 z-0"
            direction="right"
            squareColor="#2D5016"
            backgroundColor="#FFFFFF"
            gridSize={60}
            squareSize={0.4}
            fadeStart={0.15}
            fadeEnd={0.85}
            twinkleSpeed={1.0}
            twinkleStrength={0.7}
            opacity={0.8}
          />
        </div>

        {/* Left column (desktop) / content below banner (mobile) */}
        <div className="flex-1 md:w-1/2 flex flex-col justify-center px-8 sm:px-12 lg:px-16 py-12 md:py-0">

          {/* Headline */}
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-[3.75rem] text-gray-900 leading-tight mb-6">
            Cannabis<br className="hidden sm:block" />{' '}
            Education<br className="hidden sm:block" />{' '}
            &amp; Guides
          </h1>

          {/* Subtitle */}
          <p className="text-gray-600 text-lg sm:text-xl max-w-md mb-10 leading-relaxed">
            In-depth strain reviews, effect guides, and cannabis education. Find the right strain for you.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-wrap gap-4">
            <Link
              href="/articles"
              className="inline-block px-7 py-3.5 bg-leaf-600 text-white rounded-full font-medium text-sm hover:bg-leaf-700 transition-colors no-underline shadow-sm"
            >
              Browse Strains
            </Link>
            <Link
              href="/topics"
              className="inline-block px-7 py-3.5 border-2 border-leaf-600 text-leaf-700 rounded-full font-medium text-sm hover:bg-leaf-50 transition-colors no-underline"
            >
              Explore Topics
            </Link>
          </div>

        </div>
      </section>

      {/* ── Article grid — starts below the fold ───────────────────────── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
        {allPosts.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200 shadow-sm">
            <p className="text-gray-700 text-lg mb-4">
              No articles yet. Generate your first batch of content!
            </p>
            <p className="text-gray-500">
              Run: <code className="bg-gray-100 px-3 py-1 rounded text-gray-700">python content_generator.py</code>
            </p>
          </div>
        ) : (
          <HomeContent
            featuredPost={featuredPost}
            bottomPosts={bottomPosts}
            monthlyPosts={monthlyPosts}
            monthName={monthName}
          />
        )}
      </div>

    </div>
  )
}
