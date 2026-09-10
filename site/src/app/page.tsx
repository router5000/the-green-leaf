import Link from 'next/link'
import GlassTiles from '@/components/ui/GlassTiles'
import GlobeSection from '@/components/GlobeSection'
import CTASection from '@/components/CTASection'
import { Showcase2 } from '@/components/ui/Showcase2'
import { getSortedPostsData, type PostData } from '@/lib/posts'

/** Keep in sync with SHOWCASE_ITEMS in Showcase2.tsx */
const FEATURED_SLUGS = [
  'blue-dream-strain-effects-review',
  'best-strains-for-anxiety-and-stress',
  'cannabis-consumption-methods-compared',
  'how-to-germinate-cannabis-seeds',
  'organic-cannabis-soil-preparation',
] as const

const CATEGORY_LABELS: Record<string, string> = {
  'strains-genetics': 'Strains & Genetics',
  'growing-cultivation': 'Growing & Cultivation',
  'consumption-methods': 'Consumption Methods',
  'health-wellness': 'Health & Wellness',
  'legal-industry': 'Legal & Industry',
  'culture-lifestyle': 'Culture & Lifestyle',
}

/** High-intent guides to surface ahead of pure recency when not already featured. */
const HIGH_INTENT_SLUGS = [
  'most-popular-cannabis-strains-2026',
  'top-10-cannabis-strains-2026',
  'cannabis-microdosing-guide',
  'cannabis-and-sleep-science-explained',
  'high-cbd-low-thc-strains-guide',
  'entourage-effect-explained',
  'what-is-thca-flower',
  'cannabis-tolerance-explained',
  'girl-scout-cookies-strain-profile',
  'jack-herer-strain-guide',
]

function pickMoreGuides(all: PostData[], limit = 10): PostData[] {
  const featured = new Set<string>(FEATURED_SLUGS)
  const rest = all.filter(
    (p) => (p.status === 'published' || !p.status) && !featured.has(p.slug)
  )
  const bySlug = new Map(rest.map((p) => [p.slug, p]))
  const picked: PostData[] = []
  const seen = new Set<string>()

  for (const slug of HIGH_INTENT_SLUGS) {
    const post = bySlug.get(slug)
    if (post && !seen.has(post.slug)) {
      picked.push(post)
      seen.add(post.slug)
    }
  }

  // Fill with newest remaining (getSortedPostsData is newest-first).
  for (const post of rest) {
    if (picked.length >= limit) break
    if (!seen.has(post.slug)) {
      picked.push(post)
      seen.add(post.slug)
    }
  }

  return picked.slice(0, limit)
}

function MoreGuides({ posts }: { posts: PostData[] }) {
  if (posts.length === 0) return null

  return (
    <section className="bg-[#f0f0f0] px-4 sm:px-6 lg:px-8 pb-16" aria-labelledby="more-guides-heading">
      <div className="max-w-[1400px] mx-auto">
        <div className="max-w-2xl mb-8">
          <p className="text-sm sm:text-base text-neutral-600 mb-3">
            More guides
          </p>
          <h2
            id="more-guides-heading"
            className="text-2xl sm:text-3xl md:text-4xl font-medium tracking-tight text-neutral-900 leading-[1.2]"
          >
            Newest &amp; high-intent cannabis guides
          </h2>
          <p className="mt-3 text-neutral-600 text-base sm:text-lg leading-relaxed">
            Explore more strain reviews, grow how-tos, and wellness explainers beyond the featured carousel.
          </p>
        </div>

        <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-4 list-none p-0 m-0">
          {posts.map((post) => (
            <li key={post.slug} className="border-b border-neutral-200/80 pb-3">
              <Link
                href={`/articles/${post.slug}`}
                className="group no-underline block"
              >
                <span className="text-xs font-medium uppercase tracking-wide text-[#4a8c2a]">
                  {CATEGORY_LABELS[post.category ?? ''] ?? post.category ?? 'Guide'}
                </span>
                <span className="mt-1 block text-neutral-900 font-medium leading-snug group-hover:text-[#1a3a0a] transition-colors">
                  {post.title}
                </span>
              </Link>
            </li>
          ))}
        </ul>

        <div className="mt-8">
          <Link
            href="/articles"
            className="inline-flex items-center text-sm font-semibold text-[#1a3a0a] no-underline hover:underline"
          >
            Browse all articles →
          </Link>
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  const moreGuides = pickMoreGuides(getSortedPostsData(), 10)

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
              style={{ fontSize: 'clamp(2.4rem, 6.5vw, 4.5rem)' }}
            >
              Strain guides, grow tips{' '}
              <span className="text-green-300">&amp; wellness</span>
              <br className="hidden sm:block" />{' '}
              — grow smarter, consume confidently.
            </h1>
            <p className="text-white/55 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed mb-12">
              Expert cannabis education covering strain genetics, cultivation,
              consumption methods, and wellness insights — so you can learn with
              confidence.
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

      {/* ── ARTICLE SHOWCASE ─────────────────────────────────────────── */}
      <Showcase2 />

      {/* ── MORE GUIDES (crawlable inventory beyond featured five) ───── */}
      <MoreGuides posts={moreGuides} />

      <CTASection />
    </>
  )
}
