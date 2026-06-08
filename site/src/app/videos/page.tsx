import { Suspense } from 'react'
import type { Metadata } from 'next'
import type React from 'react'
import { getAllVideos } from '@/lib/posts'
import VideosTabs from '@/components/VideosTabs'
import BlinkingSquares from '@/components/ui/BlinkingSquares'

export const revalidate = 3600

const baseUrl = 'https://thegreenleaf.com'

export const metadata: Metadata = {
  title: 'Cannabis Videos - Strain Reviews, Effects & Education',
  description: 'Strain reviews, effect guides, and cannabis education from top creators.',
  openGraph: {
    title: 'Cannabis Videos - Strain Reviews, Effects & Education',
    description: 'Strain reviews, effect guides, and cannabis education from top creators.',
    url: `${baseUrl}/videos`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-default.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Strain Report - Expert Videos',
    }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cannabis Videos - Expert Tips & Tutorials',
    description: 'Strain reviews, effect guides, and cannabis education from top creators.',
    images: [`${baseUrl}/images/og-default.jpg`],
  },
  alternates: {
    canonical: `${baseUrl}/videos`,
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

export default function VideosPage() {
  const allVideos = getAllVideos()
  const uniqueChannels = Array.from(new Set(allVideos.map(v => v.channel)))

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
          squareColor="#CD201F"
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
            Cannabis Videos
          </h1>
          <p className="text-xl max-w-2xl" style={{ color: '#2d4a1e' }}>
            Strain reviews, effect guides, and cannabis education from top creators.
          </p>
          {allVideos.length > 0 && (
            <div className="mt-6 flex items-center gap-6">
              <span
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium"
                style={{ backgroundColor: 'rgba(26,58,10,0.08)', color: '#1a3a0a' }}
              >
                {allVideos.length} videos from {uniqueChannels.length} channels
              </span>
            </div>
          )}
        </div>
      </div>

      {/* ── Separator ──────────────────────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Videos — dot-panel layout ──────────────────────────────── */}
      <section className="relative bg-[#f0f0f0] overflow-hidden">
        <div className="relative grid md:grid-cols-[160px_1fr_160px]">
          {/* Left dot panel */}
          <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

          {/* Center content */}
          <div className="min-w-0 py-12">
            <div className="max-w-6xl mx-auto px-4">
              <Suspense fallback={
                <div>
                  <div className="flex flex-wrap justify-center gap-2 mb-8">
                    {Array.from({ length: 6 }).map((_, i) => (
                      <div key={i} className="h-10 w-20 bg-gray-200 rounded-full animate-pulse" />
                    ))}
                  </div>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Array.from({ length: 6 }).map((_, i) => (
                      <div key={i} className="bg-white rounded-xl shadow-md overflow-hidden">
                        <div className="aspect-video bg-gray-200 animate-pulse" />
                        <div className="p-4 space-y-3">
                          <div className="h-5 w-3/4 bg-gray-200 rounded animate-pulse" />
                          <div className="h-4 w-1/2 bg-gray-200 rounded animate-pulse" />
                          <div className="h-8 w-full bg-gray-100 rounded-lg animate-pulse" />
                          <div className="h-4 w-2/3 bg-gray-200 rounded animate-pulse" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              }>
                <VideosTabs videos={allVideos} />
              </Suspense>

              {/* Channels Section */}
              {uniqueChannels.length > 0 && (
                <div className="mt-16 pt-12 border-t border-gray-200">
                  <h2 className="text-2xl font-bold text-leaf-900 mb-6 text-center">
                    Featured Channels
                  </h2>
                  <div className="flex flex-wrap justify-center gap-3">
                    {uniqueChannels.map((channel) => {
                      const count = allVideos.filter(v => v.channel === channel).length
                      return (
                        <div
                          key={channel}
                          className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm border border-gray-200"
                        >
                          <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                          </svg>
                          <span className="text-sm font-medium text-gray-700">{channel}</span>
                          <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{count}</span>
                        </div>
                      )
                    })}
                  </div>
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
