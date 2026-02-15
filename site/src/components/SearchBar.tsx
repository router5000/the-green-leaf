'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useHeader } from './HeaderContext'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()
  const { setSearchActive } = useHeader()

  // Sync with header context
  useEffect(() => {
    setSearchActive(isExpanded)
  }, [isExpanded, setSearchActive])

  // Escape key to close
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape' && isExpanded) {
        setIsExpanded(false)
        setQuery('')
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isExpanded])

  // Lock body scroll when expanded
  useEffect(() => {
    if (isExpanded) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isExpanded])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`)
      setIsExpanded(false)
      setQuery('')
    }
  }

  const handleSearchClick = () => {
    setIsExpanded(true)
    setTimeout(() => inputRef.current?.focus(), 150)
  }

  const handleClose = () => {
    setIsExpanded(false)
    setQuery('')
  }

  return (
    <div className="relative flex items-center">
      {/* Desktop: Always show input (xl and up - 1280px) */}
      <form onSubmit={handleSubmit} className="hidden xl:flex items-center">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search articles & videos..."
            className="w-64 pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:border-leaf-500 focus:ring-1 focus:ring-leaf-500 focus:outline-none transition-all"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </form>

      {/* Mobile/Tablet: Search icon (hidden when expanded - Cancel button handles close) */}
      <AnimatePresence>
        {!isExpanded && (
          <motion.button
            key="search"
            type="button"
            onClick={handleSearchClick}
            className="xl:hidden p-2 text-gray-600 hover:text-leaf-600 transition-colors"
            aria-label="Search"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Mobile: Expanded search overlay */}
      <AnimatePresence>
        {isExpanded && (
          <>
            {/* Backdrop */}
            <motion.div
              className="xl:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={handleClose}
            />

            {/* Search Panel */}
            <motion.div
              className="xl:hidden fixed inset-x-0 top-0 z-50 bg-white shadow-xl"
              initial={{ y: '-100%' }}
              animate={{ y: 0 }}
              exit={{ y: '-100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            >
              <div className="flex items-center gap-3 p-4">
                <form onSubmit={handleSubmit} className="flex-1">
                  <div className="relative">
                    <input
                      ref={inputRef}
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Search articles & videos..."
                      className="w-full pl-10 pr-4 py-3 text-base border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:border-leaf-500 focus:ring-2 focus:ring-leaf-500/20 focus:outline-none transition-all"
                    />
                    <svg
                      className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                  </div>
                </form>
                <motion.button
                  type="button"
                  onClick={handleClose}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
                  whileTap={{ scale: 0.95 }}
                >
                  <span className="text-sm font-medium">Cancel</span>
                </motion.button>
              </div>
              <motion.p
                className="px-4 pb-4 text-sm text-gray-400"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                Search for cannabis tips, guides, and videos
              </motion.p>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
