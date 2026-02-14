'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import Image from 'next/image'
import type { VideoWithArticle } from '@/lib/posts'

const VideoModal = dynamic(() => import('./VideoModal'), { ssr: false })

interface VideosGridProps {
  videos: VideoWithArticle[]
}

export default function VideosGrid({ videos }: VideosGridProps) {
  const [selectedVideo, setSelectedVideo] = useState<VideoWithArticle | null>(null)

  if (videos.length === 0) {
    return (
      <div className="bg-gray-50 rounded-xl p-12 text-center">
        <svg
          className="w-16 h-16 mx-auto text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          No videos yet
        </h2>
        <p className="text-gray-600">
          Videos will appear here once articles are generated with YouTube content.
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video, index) => (
          <article
            key={`${video.articleSlug}-${video.id}-${index}`}
            className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 group cursor-pointer"
            onClick={() => setSelectedVideo(video)}
          >
            {/* Video Thumbnail */}
            <div className="relative aspect-video bg-gray-900">
              <Image
                src={`https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`}
                alt={video.title}
                fill
                loading="lazy"
                className="object-cover opacity-90 group-hover:opacity-100 transition-opacity"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
              />
              {/* Play Button Overlay */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
              </div>
              {/* Duration/Position Badge */}
              <div className="absolute top-3 right-3">
                <span className="px-2 py-1 bg-black/70 text-white text-xs rounded font-medium">
                  {video.position === 'hero' ? 'Featured' : 'Tutorial'}
                </span>
              </div>
            </div>

            {/* Video Info */}
            <div className="p-4">
              <h2 className="font-semibold text-gray-900 line-clamp-2 group-hover:text-grass-600 transition-colors mb-2">
                {video.title}
              </h2>

              <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
                <span>{video.channel}</span>
              </div>

              {/* Article Link */}
              <div className="bg-grass-50 rounded-lg px-3 py-2">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-grass-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm text-grass-700 font-medium line-clamp-1">
                    {video.articleTitle}
                  </span>
                </div>
              </div>

              {/* Key Insight Preview */}
              {video.insights?.best_quote && (
                <p className="text-sm text-gray-600 mt-3 italic line-clamp-2">
                  &ldquo;{video.insights.best_quote.slice(0, 100)}...&rdquo;
                </p>
              )}

              {/* Season Tag */}
              <div className="mt-3 flex items-center gap-2">
                <span className="text-xs bg-grass-100 text-grass-700 px-2 py-1 rounded-full capitalize">
                  {video.articleSeason}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>

      {/* Video Modal */}
      {selectedVideo && (
        <VideoModal
          video={selectedVideo}
          articleSlug={selectedVideo.articleSlug}
          articleTitle={selectedVideo.articleTitle}
          onClose={() => setSelectedVideo(null)}
        />
      )}
    </>
  )
}
