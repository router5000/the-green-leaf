'use client'

import { useState, useMemo, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import type { PostData } from '@/lib/posts'

// Month-to-season mapping
const MONTH_SEASONS: Record<number, string[]> = {
  0:  ['winter'],           // January
  1:  ['winter', 'spring'], // February
  2:  ['spring'],           // March
  3:  ['spring'],           // April
  4:  ['spring', 'summer'], // May
  5:  ['summer'],           // June
  6:  ['summer'],           // July
  7:  ['summer', 'fall'],   // August
  8:  ['fall'],             // September
  9:  ['fall'],             // October
  10: ['fall', 'winter'],   // November
  11: ['winter'],           // December
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

interface ArticlesTabsProps {
  posts: PostData[]
}

const ARTICLES_PER_PAGE = 12

export default function ArticlesTabs({ posts }: ArticlesTabsProps) {
  const searchParams = useSearchParams()
  const currentMonth = new Date().getMonth()
  const monthName = MONTH_NAMES[currentMonth]
  const monthSeasons = MONTH_SEASONS[currentMonth]
  const hasInteracted = useRef(false)
  const [visibleCount, setVisibleCount] = useState(ARTICLES_PER_PAGE)

  const tabs = [
    { id: 'all', label: 'All' },
    { id: 'monthly', label: `For ${monthName}` },
    { id: 'spring', label: 'Spring' },
    { id: 'summer', label: 'Summer' },
    { id: 'fall', label: 'Fall' },
    { id: 'winter', label: 'Winter' },
  ]

  const initialTab = searchParams.get('tab') || 'all'
  const [activeTab, setActiveTab] = useState(initialTab)

  const handleTabClick = (tabId: string) => {
    hasInteracted.current = true
    setActiveTab(tabId)
    setVisibleCount(ARTICLES_PER_PAGE)
  }

  const filteredPosts = useMemo(() => {
    if (activeTab === 'all') return posts
    if (activeTab === 'monthly') {
      return posts.filter(post =>
        monthSeasons.includes(post.season?.toLowerCase())
      )
    }
    return posts.filter(post =>
      post.season?.toLowerCase() === activeTab
    )
  }, [posts, activeTab, monthSeasons])

  const visiblePosts = filteredPosts.slice(0, visibleCount)
  const hasMore = visibleCount < filteredPosts.length

  return (
    <div>
      {/* Tabs */}
      <motion.nav
        aria-label="Article filters"
        className="flex flex-wrap justify-center gap-2 mb-8"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div role="tablist" aria-label="Filter articles by season" className="flex flex-wrap justify-center gap-2">
          {tabs.map((tab, index) => (
            <motion.button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls="articles-panel"
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

      {/* Articles List */}
      {filteredPosts.length === 0 ? (
        <motion.div
          className="bg-leaf-50 rounded-lg p-8 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-leaf-700 text-lg">
            No articles found for this filter.
          </p>
        </motion.div>
      ) : (
        <motion.div
          id="articles-panel"
          role="tabpanel"
          aria-label={`${activeTab === 'all' ? 'All' : activeTab === 'monthly' ? `${monthName}` : activeTab} articles`}
          className="space-y-8"
          layout
        >
          <AnimatePresence mode="popLayout">
            {visiblePosts.map((post, index) => (
              <motion.article
                key={post.slug}
                layout
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
                transition={{
                  duration: hasInteracted.current ? 0.3 : 0.4,
                  delay: hasInteracted.current ? 0 : index * 0.08,
                  layout: { duration: 0.3 }
                }}
                viewport={{ once: true, margin: "-50px" }}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow group"
              >
                <div className="md:flex">
                  {/* Thumbnail Image */}
                  {post.featured_image && (
                    <div className="md:w-80 md:flex-shrink-0">
                      <div className="relative h-64 md:h-full overflow-hidden">
                        <Image
                          src={post.featured_image}
                          alt={post.featured_image_alt || post.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-700"
                          sizes="(max-width: 768px) 100vw, 320px"
                        />
                        <div
                          className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                          style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.5), rgba(227,191,112,0.5))' }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Content */}
                  <div className="p-6 flex-1">
                    <div className="flex flex-wrap items-center gap-3 text-sm text-leaf-600 mb-3">
                      <span className="bg-leaf-100 px-3 py-1 rounded-full font-medium">
                        {post.season}
                      </span>
                      {post.last_updated && (Date.now() - new Date(post.last_updated).getTime()) < 14 * 86400000 && (
                        <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-semibold">
                          Recently Updated
                        </span>
                      )}
                      <span>{post.estimated_read_time}</span>
                    </div>

                    <h2 className="text-2xl font-semibold text-leaf-900 mb-3 line-clamp-1">
                      <Link
                        href={`/articles/${post.slug}`}
                        className="hover:text-leaf-600 transition"
                      >
                        {post.title}
                      </Link>
                    </h2>

                    <p className="text-gray-600 mb-4 line-clamp-2">
                      {post.meta_description}
                    </p>

                    <div className="flex items-center justify-end">
                      <Link
                        href={`/articles/${post.slug}`}
                        className="text-leaf-600 hover:text-leaf-800 font-medium text-sm whitespace-nowrap"
                        aria-label={`Read full article: ${post.title}`}
                      >
                        Read More →
                      </Link>
                    </div>
                  </div>
                </div>
              </motion.article>
            ))}
          </AnimatePresence>

          {hasMore && (
            <motion.div
              className="text-center pt-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <button
                onClick={() => setVisibleCount(prev => prev + ARTICLES_PER_PAGE)}
                className="px-8 py-3 bg-leaf-600 text-white rounded-full font-medium hover:bg-leaf-700 transition-colors"
              >
                Show More Articles ({filteredPosts.length - visibleCount} remaining)
              </button>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  )
}
