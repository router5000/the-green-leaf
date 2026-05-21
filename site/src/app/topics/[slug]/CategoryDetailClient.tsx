'use client'

import Link from 'next/link'
import Image from 'next/image'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import type React from 'react'

interface PostSummary {
  slug: string
  title: string
  meta_description: string
  featured_image: string | null
  featured_image_alt: string | null
  tags: string[]
  estimated_read_time: string
  category: string | null
}

interface ClusterInfo {
  id: string
  title: string
  description: string
  color: string
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

const ALL_TOPIC_IMAGES = [
  'strains-genetics',
  'growing-cultivation',
  'consumption-methods',
  'health-wellness',
  'legal-industry',
  'culture-lifestyle',
].map(id => `/images/topics/${id}.jpg`)

function resolveImages(clusterId: string, posts: PostSummary[]): string[] {
  // Build fallback pool: category image first, then other topic images
  const fallbacks = [
    `/images/topics/${clusterId}.jpg`,
    ...ALL_TOPIC_IMAGES.filter(img => img !== `/images/topics/${clusterId}.jpg`),
  ]
  const used = new Set<string>()
  let fallbackIdx = 0

  return posts.map(post => {
    const img = post.featured_image
    if (img && !used.has(img)) {
      used.add(img)
      return img
    }
    // Find next unused fallback
    while (fallbackIdx < fallbacks.length && used.has(fallbacks[fallbackIdx])) {
      fallbackIdx++
    }
    const chosen = fallbackIdx < fallbacks.length ? fallbacks[fallbackIdx] : fallbacks[0]
    used.add(chosen)
    fallbackIdx++
    return chosen
  })
}

export default function CategoryDetailClient({
  cluster,
  posts,
}: {
  cluster: ClusterInfo
  posts: PostSummary[]
}) {
  const resolvedImages = resolveImages(cluster.id, posts)
  return (
    <div className="bg-[#f0f0f0]">
      {/* ── Separator — below nav bar ──────────────────────────────── */}
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
          squareColor="#4a8c2a"
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
          {/* ← Back link */}
          <Link
            href="/topics"
            className="inline-flex items-center gap-1.5 text-sm font-medium mb-6 hover:opacity-70 transition-opacity"
            style={{ color: '#1a3a0a' }}
          >
            ← All Topics
          </Link>

          <h1
            className="text-4xl md:text-5xl font-bold mb-4"
            style={{ color: '#1a3a0a' }}
          >
            {cluster.title}
          </h1>
          <p className="text-xl max-w-2xl" style={{ color: '#2d4a1e' }}>
            {cluster.description}
          </p>

          {/* Stats row */}
          <div className="mt-6 flex items-center gap-6">
            <span
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium"
              style={{ backgroundColor: 'rgba(26,58,10,0.08)', color: '#1a3a0a' }}
            >
              {posts.length} {posts.length === 1 ? 'article' : 'articles'}
            </span>
          </div>
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
            <h2 className="text-2xl font-bold text-neutral-900 mb-8">
              Articles in {cluster.title}
            </h2>

            {posts.length === 0 ? (
              <div className="rounded-xl border border-[#d4d4d4] bg-white/60 p-12 text-center">
                <p className="text-neutral-500 text-lg">
                  More guides coming soon — check back shortly.
                </p>
                <Link
                  href="/topics"
                  className="mt-6 inline-block text-sm font-medium text-leaf-600 hover:text-leaf-800"
                >
                  ← Browse all topics
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                {posts.map((post, index) => (
                  <Link
                    key={post.slug}
                    href={`/articles/${post.slug}`}
                    className="no-underline block group"
                  >
                    <article className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-300 md:flex">
                      {/* Thumbnail */}
                      <div className="md:w-64 md:flex-shrink-0">
                        <div className="relative h-48 md:h-full overflow-hidden">
                            <Image
                              src={resolvedImages[index]}
                              alt={post.featured_image_alt || post.title}
                              fill
                              className="object-cover group-hover:scale-105 transition-transform duration-500"
                              sizes="(max-width: 768px) 100vw, 256px"
                            />
                        </div>
                      </div>
                      {/* Content */}
                      <div className="p-6 flex-1">
                        <div className="flex flex-wrap gap-2 mb-3">
                          {post.tags.slice(0, 3).map(tag => (
                            <span
                              key={tag}
                              className="bg-leaf-100 text-leaf-700 px-3 py-0.5 rounded-full text-xs font-medium"
                            >
                              {tag}
                            </span>
                          ))}
                          <span className="text-xs text-neutral-400">{post.estimated_read_time}</span>
                        </div>
                        <h3 className="text-lg font-semibold text-neutral-900 mb-2 group-hover:text-leaf-700 transition-colors line-clamp-2">
                          {post.title}
                        </h3>
                        <p className="text-neutral-500 text-sm line-clamp-2">
                          {post.meta_description}
                        </p>
                        <span className="mt-4 inline-block text-sm font-medium text-leaf-600 group-hover:text-leaf-800 transition-colors">
                          Read article →
                        </span>
                      </div>
                    </article>
                  </Link>
                ))}
              </div>
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
