import { Suspense } from 'react'
import { getSortedPostsData } from '@/lib/posts'
import ArticlesTabs from '@/components/ArticlesTabs'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import type { Metadata } from 'next'
import type React from 'react'

export const revalidate = 3600

const baseUrl = 'https://thegreenleaf.com'

export const metadata: Metadata = {
  title: 'Cannabis Articles & Guides - Strain Reviews, Effects & Education',
  description: 'In-depth strain reviews, effect guides, and cannabis education. Find the right strain for you.',
  openGraph: {
    title: 'Cannabis Articles & Guides - The Strain Report',
    description: 'In-depth strain reviews, effect guides, and cannabis education. Find the right strain for you.',
    url: `${baseUrl}/articles`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-articles.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Strain Report - Expert Cannabis Articles',
    }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'All Cannabis Articles & Guides',
    description: 'In-depth strain reviews, effect guides, and cannabis education. Find the right strain for you.',
    images: [`${baseUrl}/images/og-articles.jpg`],
  },
  alternates: {
    canonical: `${baseUrl}/articles`,
  },
}

function VerticalDash({ side }: { side: 'left' | 'right' }) {
  return (
    <div
      className={`absolute ${side}-[160px] top-0 bottom-0 hidden md:block pointer-events-none`}
      aria-hidden="true"
    >
      <svg width="1" height="100%" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <line x1="0.5" y1="0" x2="0.5" y2="100%" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>
    </div>
  )
}

const dotGridStyle: React.CSSProperties = {
  backgroundImage: 'radial-gradient(circle, #c8c8c8 1px, transparent 1px)',
  backgroundSize: '20px 20px',
  backgroundColor: '#f0f0f0',
}

export default function ArticlesPage() {
  const allPosts = getSortedPostsData()

  return (
    <div className="bg-[#f0f0f0]">
      {/* ── Separator — below nav bar ───────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Hero ───────────────────────────────────────────────────── */}
      <div className="relative py-16 overflow-hidden">
        <BlinkingSquares
          className="absolute inset-0"
          width="100%"
          height="100%"
          direction="right"
          gridSize={52}
          squareColor="#BB29FF"
          backgroundColor="#f0f0f0"
          falloff={1.25}
          fadeStart={0.33}
          fadeEnd={1}
          squareSize={0.57}
          minBrightness={0.55}
          twinkleSpeed={1.4}
          twinkleStrength={0.94}
          intensity={1}
          opacity={0.4}
          dpr={1.5}
        />
        <div className="relative z-10 max-w-6xl mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#1a3a0a' }}>
            Cannabis Articles &amp; Guides
          </h1>
          <p className="text-xl max-w-2xl" style={{ color: '#2d4a1e' }}>
            In-depth strain reviews, effect guides, and cannabis education. Find the right strain for you.
          </p>
        </div>
      </div>

      {/* ── Separator ──────────────────────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Articles — dot-panel layout ────────────────────────────── */}
      <section className="relative bg-[#f0f0f0] overflow-hidden">
        <div className="relative grid md:grid-cols-[160px_1fr_160px]">
          {/* Left dot panel */}
          <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

          {/* Center content */}
          <div className="min-w-0 py-12">
            <div className="max-w-6xl mx-auto px-4">
              {allPosts.length === 0 ? (
                <div className="bg-leaf-50 rounded-lg p-8 text-center">
                  <p className="text-leaf-700 text-lg mb-4">No articles published yet.</p>
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
          </div>

          {/* Right dot panel */}
          <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

          <VerticalDash side="left" />
          <VerticalDash side="right" />
        </div>
      </section>

      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>
    </div>
  )
}
