import Link from 'next/link'
import { getSortedPostsData, getMonthlyPosts } from '@/lib/posts'
import HomeContent from '@/components/HomeContent'
import GlassTiles from '@/components/ui/GlassTiles'
import GlobeSection from '@/components/GlobeSection'
import CTASection from '@/components/CTASection'

export default function Home() {
  const allPosts = getSortedPostsData()
  const featuredPost = allPosts[0]
  const { posts: monthlyPosts, monthName } = getMonthlyPosts(3)
  const bottomPosts = allPosts.slice(4, 6)

  return (
    <>
      {/* ── Separator — below nav bar ───────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── HERO CARD ───────────────────────────────────────────────── */}
      <div className="bg-[#f0f0f0] px-4 sm:px-5 pt-4 sm:pt-5 pb-4 sm:pb-5">
        <section
          className="relative flex flex-col items-center justify-center overflow-hidden rounded-2xl"
          style={{ minHeight: 'calc(100vh - 5.5rem)' }}
        >
          {/* GlassTiles WebGL background */}
          <GlassTiles
            colorA="#0a2405"
            colorB="#2d6a0f"
            backgroundColor="#061502"
            speed={0.25}
            tileDensity={3}
            rippleLayers={5}
            warpStrength={0.33}
            bandSharpness={3}
            chromaticSpread={0}
            opacity={0.6}
            dpr={1.5}
            width="100%"
            height="100%"
            className="absolute inset-0"
          />

          {/* Hero content */}
          <div className="relative z-10 text-center px-4 sm:px-6 max-w-4xl mx-auto">
            <p className="text-green-300/70 text-sm sm:text-base font-medium tracking-widest uppercase mb-6 select-none">
              Cannabis Education Resource
            </p>
            <h1
              className="font-serif font-bold text-white leading-[1.06] tracking-tight mb-7"
              style={{ fontSize: 'clamp(2.75rem, 7vw, 5rem)' }}
            >
              Grow smarter,<br className="hidden sm:block" />{' '}
              consume{' '}
              <span className="text-green-300">confidently.</span>
            </h1>
            <p className="text-white/55 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed mb-12">
              Your comprehensive cannabis education resource — strain guides,
              growing tips, wellness insights and more.
            </p>
            <Link
              href="/topics"
              className="inline-block px-9 py-4 bg-white text-[#0d2106] rounded-full font-semibold text-base hover:bg-green-50 transition-colors no-underline shadow-2xl"
            >
              Explore Topics
            </Link>
          </div>
        </section>
      </div>

      {/* ── GLOBE SECTION ───────────────────────────────────────────── */}
      <GlobeSection />

      {/* ── ARTICLE CARDS ───────────────────────────────────────────── */}
      <div className="bg-[#f0f0f0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          {allPosts.length === 0 ? (
            <div className="rounded-xl p-12 text-center border border-gray-200">
              <p className="text-gray-700 text-lg mb-4">
                No articles yet. Generate your first batch of content!
              </p>
              <p className="text-gray-500">
                Run:{' '}
                <code className="bg-gray-100 px-3 py-1 rounded text-gray-700">
                  python content_generator.py
                </code>
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

      <CTASection />
    </>
  )
}
