'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'

interface VideoModalProps {
  video: {
    id: string
    title: string
    channel: string
    insights?: {
      key_points?: string[]
      best_quote?: string
      pro_tips?: string[]
    }
  }
  articleSlug: string
  articleTitle: string
  onClose: () => void
}

export default function VideoModal({ video, articleSlug, articleTitle, onClose }: VideoModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  // Lock body scroll and handle escape key
  useEffect(() => {
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    // Focus close button on mount
    closeButtonRef.current?.focus()

    return () => {
      document.body.style.overflow = originalOverflow
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [onClose])

  // Close on backdrop click
  function handleBackdropClick(e: React.MouseEvent) {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const hasInsights = video.insights && (
    video.insights.best_quote ||
    (video.insights.key_points && video.insights.key_points.length > 0) ||
    (video.insights.pro_tips && video.insights.pro_tips.length > 0)
  )

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 animate-fade-in"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-white rounded-xl shadow-2xl"
      >
        {/* Close button */}
        <button
          ref={closeButtonRef}
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-black/50 hover:bg-black/70 text-white rounded-full transition"
          aria-label="Close video"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* YouTube Video Embed */}
        <div className="relative aspect-video bg-black">
          <iframe
            src={`https://www.youtube.com/embed/${video.id}?autoplay=1&rel=0`}
            title={video.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="absolute inset-0 w-full h-full"
          />
        </div>

        {/* Video Info */}
        <div className="p-6">
          <h2 id="modal-title" className="text-xl font-bold text-gray-900 mb-2">
            {video.title}
          </h2>

          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-4">
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              <span>{video.channel}</span>
            </div>
            <span className="text-gray-300">|</span>
            <Link
              href={`/articles/${articleSlug}`}
              className="text-grass-600 hover:text-grass-700 font-medium hover:underline"
              onClick={onClose}
            >
              View full article: {articleTitle}
            </Link>
          </div>

          {/* Transcript Insights */}
          {hasInsights && (
            <div className="border-t border-gray-200 pt-5 mt-2 space-y-5">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Video Highlights
              </h3>

              {/* Best Quote */}
              {video.insights?.best_quote && (
                <blockquote className="bg-grass-50 border-l-4 border-grass-500 px-4 py-3 rounded-r-lg">
                  <p className="text-gray-700 italic">
                    "{video.insights.best_quote}"
                  </p>
                </blockquote>
              )}

              {/* Key Points */}
              {video.insights?.key_points && video.insights.key_points.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 font-semibold text-gray-900 mb-2">
                    <span className="text-lg">📝</span> Key Points
                  </h4>
                  <ul className="space-y-2">
                    {video.insights.key_points.slice(0, 4).map((point, i) => (
                      <li key={i} className="flex gap-2 text-gray-700">
                        <span className="text-grass-600 mt-1">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Pro Tips */}
              {video.insights?.pro_tips && video.insights.pro_tips.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 font-semibold text-gray-900 mb-2">
                    <span className="text-lg">💡</span> Pro Tips
                  </h4>
                  <ul className="space-y-2">
                    {video.insights.pro_tips.slice(0, 3).map((tip, i) => (
                      <li key={i} className="flex gap-2 text-gray-700">
                        <span className="text-amber-500 mt-1">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
