import { Suspense } from 'react'
import type { Metadata } from 'next'
import { getAllVideos } from '@/lib/posts'
import VideosTabs from '@/components/VideosTabs'

export const revalidate = 3600 // Revalidate every hour

const baseUrl = 'https://thegreenleaf.com'

export const metadata: Metadata = {
  title: 'Cannabis Videos - Strain Reviews, Effects & Education',
  description: 'Strain reviews, effect guides, and cannabis education from top creators.',
  openGraph: {
    title: 'Cannabis Videos - Strain Reviews, Effects & Education',
    description: 'Strain reviews, effect guides, and cannabis education from top creators.',
    url: `${baseUrl}/videos`,
    siteName: 'The Green Leaf',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-default.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Green Leaf - Expert Videos',
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

export default function VideosPage() {
  const allVideos = getAllVideos()

  // Group videos by channel for variety display
  const uniqueChannels = Array.from(new Set(allVideos.map(v => v.channel)))

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Page Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-serif text-gray-900 mb-8">
          Cannabis Videos
        </h1>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-4">
          Strain reviews, effect guides, and cannabis education from top creators.
        </p>
        <span className="text-sm text-gray-500">{allVideos.length} videos from {uniqueChannels.length} channels</span>
      </div>

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
  )
}
