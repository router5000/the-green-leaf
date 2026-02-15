'use client'

import { useState, type ReactNode } from 'react'
import dynamic from 'next/dynamic'
import Link from 'next/link'
import Image from 'next/image'
import type { ArticleSearchResult, VideoSearchResult } from '@/lib/search'

const VideoModal = dynamic(() => import('./VideoModal'), { ssr: false })

interface SearchResultsProps {
  articles: ArticleSearchResult[]
  videos: VideoSearchResult[]
  query: string
}

function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * Highlight matching terms in text using React elements (XSS-safe)
 */
function HighlightMatch({ text, query }: { text: string; query: string }): ReactNode {
  if (!query.trim()) return text

  const terms = query.trim().split(/\s+/).filter(Boolean).map(escapeRegExp)
  const pattern = new RegExp(`(${terms.join('|')})`, 'gi')
  const parts = text.split(pattern)

  return parts.map((part, i) =>
    pattern.test(part) ? (
      <mark key={i} className="bg-yellow-200 px-0.5 rounded">{part}</mark>
    ) : (
      part
    )
  )
}

const RESULTS_PER_PAGE = 12

export default function SearchResults({ articles, videos, query }: SearchResultsProps) {
  const [activeTab, setActiveTab] = useState<'articles' | 'videos'>(
    articles.length > 0 ? 'articles' : 'videos'
  )
  const [selectedVideo, setSelectedVideo] = useState<VideoSearchResult | null>(null)
  const [visibleArticles, setVisibleArticles] = useState(RESULTS_PER_PAGE)
  const [visibleVideos, setVisibleVideos] = useState(RESULTS_PER_PAGE)

  return (
    <div>
      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('articles')}
          className={`flex items-center gap-2 px-6 py-3 font-medium text-sm transition-colors relative ${
            activeTab === 'articles'
              ? 'text-leaf-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Articles
          <span className={`px-2 py-0.5 rounded-full text-xs ${
            activeTab === 'articles'
              ? 'bg-leaf-100 text-leaf-700'
              : 'bg-gray-100 text-gray-600'
          }`}>
            {articles.length}
          </span>
          {activeTab === 'articles' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-leaf-600" />
          )}
        </button>

        <button
          onClick={() => setActiveTab('videos')}
          className={`flex items-center gap-2 px-6 py-3 font-medium text-sm transition-colors relative ${
            activeTab === 'videos'
              ? 'text-leaf-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          Videos
          <span className={`px-2 py-0.5 rounded-full text-xs ${
            activeTab === 'videos'
              ? 'bg-leaf-100 text-leaf-700'
              : 'bg-gray-100 text-gray-600'
          }`}>
            {videos.length}
          </span>
          {activeTab === 'videos' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-leaf-600" />
          )}
        </button>
      </div>

      {/* Articles Tab Content */}
      {activeTab === 'articles' && (
        <div className="space-y-6">
          {articles.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p>No articles found for &ldquo;{query}&rdquo;</p>
              {videos.length > 0 && (
                <button
                  onClick={() => setActiveTab('videos')}
                  className="mt-2 text-leaf-600 hover:text-leaf-700 font-medium"
                >
                  View {videos.length} video{videos.length !== 1 ? 's' : ''} instead →
                </button>
              )}
            </div>
          ) : (
            <>
              {articles.slice(0, visibleArticles).map((article) => (
                <article
                  key={article.slug}
                  className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition group"
                >
                  <Link href={`/articles/${article.slug}`} className="md:flex">
                    {article.featured_image && (
                      <div className="md:w-64 md:flex-shrink-0">
                        <div className="relative h-48 md:h-full">
                          <Image
                            src={article.featured_image}
                            alt={article.featured_image_alt || article.title}
                            fill
                            className="object-cover group-hover:scale-105 transition-transform duration-500"
                            sizes="(max-width: 768px) 100vw, 256px"
                          />
                        </div>
                      </div>
                    )}
                    <div className="p-6 flex-1">
                      <div className="flex flex-wrap items-center gap-2 text-sm text-leaf-600 mb-2">
                        <span className="bg-leaf-100 px-2 py-0.5 rounded-full text-xs font-medium">
                          {article.season}
                        </span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-500">{article.estimated_read_time}</span>
                      </div>
                      <h3 className="text-xl font-semibold text-leaf-900 mb-2 group-hover:text-leaf-600 transition">
                        <HighlightMatch text={article.title} query={query} />
                      </h3>
                      <p className="text-gray-600 text-sm line-clamp-2">
                        <HighlightMatch text={article.meta_description} query={query} />
                      </p>
                    </div>
                  </Link>
                </article>
              ))}
              {visibleArticles < articles.length && (
                <div className="text-center pt-4">
                  <button
                    onClick={() => setVisibleArticles(v => v + RESULTS_PER_PAGE)}
                    className="px-6 py-3 bg-leaf-600 text-white rounded-full font-medium hover:bg-leaf-700 transition-colors"
                  >
                    Show More Articles ({articles.length - visibleArticles} remaining)
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Videos Tab Content */}
      {activeTab === 'videos' && (
        <div>
          {videos.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p>No videos found for &ldquo;{query}&rdquo;</p>
              {articles.length > 0 && (
                <button
                  onClick={() => setActiveTab('articles')}
                  className="mt-2 text-leaf-600 hover:text-leaf-700 font-medium"
                >
                  View {articles.length} article{articles.length !== 1 ? 's' : ''} instead →
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="grid md:grid-cols-2 gap-6">
                {videos.slice(0, visibleVideos).map((video) => (
                  <article
                    key={`${video.articleSlug}-${video.id}`}
                    className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition group cursor-pointer"
                    onClick={() => setSelectedVideo(video)}
                  >
                    <div className="relative aspect-video bg-gray-900">
                      <Image
                        src={`https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`}
                        alt={video.title}
                        fill
                        className="object-cover opacity-90 group-hover:opacity-100 transition"
                        sizes="(max-width: 768px) 100vw, 50vw"
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                          <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z"/>
                          </svg>
                        </div>
                      </div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2 group-hover:text-leaf-600 transition">
                        <HighlightMatch text={video.title} query={query} />
                      </h3>
                      <p className="text-sm text-gray-500 mb-2">{video.channel}</p>
                      <div className="text-xs text-gray-600 bg-gray-50 rounded px-2 py-1">
                        From: <span className="text-leaf-700 font-medium">{video.articleTitle}</span>
                      </div>
                      {video.insights?.best_quote && (
                        <p className="text-sm text-gray-600 mt-3 italic line-clamp-2">
                          &ldquo;<HighlightMatch text={video.insights.best_quote.slice(0, 100)} query={query} />&hellip;&rdquo;
                        </p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
              {visibleVideos < videos.length && (
                <div className="text-center pt-6">
                  <button
                    onClick={() => setVisibleVideos(v => v + RESULTS_PER_PAGE)}
                    className="px-6 py-3 bg-leaf-600 text-white rounded-full font-medium hover:bg-leaf-700 transition-colors"
                  >
                    Show More Videos ({videos.length - visibleVideos} remaining)
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Video Modal */}
      {selectedVideo && (
        <VideoModal
          video={selectedVideo}
          articleSlug={selectedVideo.articleSlug}
          articleTitle={selectedVideo.articleTitle}
          onClose={() => setSelectedVideo(null)}
        />
      )}
    </div>
  )
}
