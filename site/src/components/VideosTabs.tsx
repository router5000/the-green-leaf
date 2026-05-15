'use client'

import { useState, useMemo, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import dynamic from 'next/dynamic'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import type { VideoWithArticle } from '@/lib/posts'

const VideoModal = dynamic(() => import('./VideoModal'), { ssr: false })

interface VideosTabsProps {
  videos: VideoWithArticle[]
}

const tabs = [
  { id: 'all',            label: 'All' },
  { id: 'strain-reviews', label: 'Strain Reviews' },
  { id: 'by-effect',      label: 'By Effect' },
  { id: 'indica-sativa',  label: 'Indica / Sativa / Hybrid' },
  { id: 'science',        label: 'Science & Education' },
  { id: 'consumption',    label: 'Consumption Methods' },
]

function matchesTab(video: VideoWithArticle, tabId: string): boolean {
  const tags = video.articleTags.map(t => t.toLowerCase())
  const text = `${video.title} ${video.articleTitle} ${video.articleKeyword}`.toLowerCase()

  switch (tabId) {
    case 'strain-reviews':
      return tags.some(t =>
        ['strain profile', 'strain guide', 'strain review', 'strain effects',
         'strain overview', 'strain breakdown'].includes(t)
      ) || /strain.*(profile|guide|review|effects|breakdown)|review.*strain/.test(text)

    case 'by-effect':
      return tags.some(t =>
        ['anxiety', 'sleep', 'pain', 'focus', 'stress relief', 'depression',
         'insomnia', 'relaxation', 'energy', 'appetite', 'nausea', 'ptsd',
         'inflammation', 'migraines', 'mood', 'creativity'].some(e => t.includes(e))
      ) || /\b(anxiety|sleep|pain|focus|stress|depression|insomnia|relaxation|energy|appetite|nausea|ptsd|inflammation|migraine|mood|creativity)\b/.test(text)

    case 'indica-sativa':
      return tags.some(t => ['indica', 'sativa', 'hybrid'].includes(t))
        || /\b(indica|sativa|hybrid)\b/.test(text)

    case 'science':
      return tags.some(t =>
        ['terpenes', 'terpene', 'cannabinoids', 'cannabinoid', 'endocannabinoid',
         'entourage effect', 'thc', 'cbd', 'thca', 'cbg', 'cbn', 'pharmacology',
         'lab results', 'beginner cannabis'].some(s => t.includes(s))
      ) || /\b(terpene|cannabinoid|endocannabinoid|entourage|thc|cbd|thca|pharmacology|science|explained|what is|how does)\b/.test(text)

    case 'consumption':
      return tags.some(t =>
        ['vaping', 'vaporizer', 'edibles', 'tincture', 'concentrates', 'pre-roll',
         'topical', 'dabs', 'dabbing', 'live resin', 'rosin', 'hash', 'smoking',
         'bong', 'joint', 'blunt', 'pipe'].some(c => t.includes(c))
      ) || /\b(vap|edible|tincture|concentrat|pre.?roll|topical|dab|smok|bong|pipe|joint|blunt|hash|rosin|live resin|consume|consumption)\b/.test(text)

    default:
      return true
  }
}

export default function VideosTabs({ videos }: VideosTabsProps) {
  const searchParams = useSearchParams()
  const hasInteracted = useRef(false)
  const [selectedVideo, setSelectedVideo] = useState<VideoWithArticle | null>(null)

  const initialTab = searchParams.get('tab') || 'all'
  const [activeTab, setActiveTab] = useState(initialTab)

  const handleTabClick = (tabId: string) => {
    hasInteracted.current = true
    setActiveTab(tabId)
  }

  const filteredVideos = useMemo(() => {
    if (activeTab === 'all') return videos
    return videos.filter(video => matchesTab(video, activeTab))
  }, [videos, activeTab])

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
      <div>
        {/* Tabs */}
        <motion.nav
          aria-label="Video filters"
          className="flex flex-wrap justify-center gap-2 mb-8"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div role="tablist" aria-label="Filter videos by category" className="flex flex-wrap justify-center gap-2">
            {tabs.map((tab, index) => (
              <motion.button
                key={tab.id}
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls="videos-panel"
                onClick={() => handleTabClick(tab.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-leaf-600 text-white'
                    : 'bg-leaf-100 text-leaf-700 hover:bg-leaf-200'
                }`}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {tab.label}
              </motion.button>
            ))}
          </div>
        </motion.nav>

        {/* Videos Grid */}
        {filteredVideos.length === 0 ? (
          <motion.div
            className="bg-leaf-50 rounded-lg p-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <p className="text-leaf-700 text-lg">
              No videos found for this filter.
            </p>
          </motion.div>
        ) : (
          <motion.div
            id="videos-panel"
            role="tabpanel"
            aria-label={`${tabs.find(t => t.id === activeTab)?.label ?? 'All'} videos`}
            className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6"
            layout
          >
            <AnimatePresence mode="popLayout">
              {filteredVideos.map((video, index) => (
                <motion.article
                  key={`${video.articleSlug}-${video.id}-${index}`}
                  layout
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
                  transition={{
                    duration: hasInteracted.current ? 0.3 : 0.4,
                    delay: hasInteracted.current ? 0 : index * 0.06,
                    layout: { duration: 0.3 }
                  }}
                  viewport={{ once: true, margin: "-50px" }}
                  className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 group cursor-pointer"
                  onClick={() => setSelectedVideo(video)}
                >
                  {/* Video Thumbnail */}
                  <div className="relative aspect-video bg-gray-900 overflow-hidden">
                    <Image
                      src={`https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`}
                      alt={video.title}
                      fill
                      loading="lazy"
                      className="object-cover opacity-90 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700"
                      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    />
                    <div
                      className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                      style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.5), rgba(227,191,112,0.5))' }}
                    />
                    {/* Play Button Overlay */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                        <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8 5v14l11-7z"/>
                        </svg>
                      </div>
                    </div>
                    {/* Position Badge */}
                    <div className="absolute top-3 right-3">
                      <span className="px-2 py-1 bg-black/70 text-white text-xs rounded font-medium">
                        {video.position === 'hero' ? 'Featured' : 'Related'}
                      </span>
                    </div>
                  </div>

                  {/* Video Info */}
                  <div className="p-4">
                    <h2 className="font-semibold text-gray-900 line-clamp-2 group-hover:text-leaf-600 transition-colors mb-2">
                      {video.title}
                    </h2>

                    <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                      <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                      </svg>
                      <span>{video.channel}</span>
                    </div>

                    {/* Article Link */}
                    <div className="bg-leaf-50 rounded-lg px-3 py-2">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-leaf-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="text-sm text-leaf-700 font-medium line-clamp-1">
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

                    {/* Tags */}
                    {video.articleTags.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {video.articleTags.slice(0, 3).map(tag => (
                          <span key={tag} className="text-xs bg-leaf-100 text-leaf-700 px-2 py-0.5 rounded-full capitalize">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.article>
              ))}
            </AnimatePresence>
          </motion.div>
        )}
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
