'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useHeader } from './HeaderContext'

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/topics', label: 'Topics' },
  { href: '/articles', label: 'Articles' },
  { href: '/videos', label: 'Videos' },
]

export default function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const { isSearchActive } = useHeader()
  const navRef = useRef<HTMLElement>(null)

  // Close menu on route change
  useEffect(() => {
    setIsOpen(false)
  }, [pathname])

  // Lock body scroll and trap focus when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'

      // Focus trap: keep Tab within the nav drawer
      const nav = navRef.current
      if (!nav) return

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          setIsOpen(false)
          return
        }
        if (e.key !== 'Tab') return

        const focusable = nav.querySelectorAll<HTMLElement>(
          'a[href], button, [tabindex]:not([tabindex="-1"])'
        )
        const first = focusable[0]
        const last = focusable[focusable.length - 1]

        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault()
          last.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }

      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname === href || pathname.startsWith(`${href}/`)
  }

  // Hide when search is active
  if (isSearchActive) {
    return null
  }

  return (
    <div className="sm:hidden">
      {/* Hamburger / Close Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 w-10 h-10 text-gray-600 hover:text-leaf-600 transition-colors z-50"
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={isOpen}
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-4">
          {/* Top bar */}
          <motion.span
            className="absolute left-0 w-5 h-0.5 bg-current rounded-full"
            initial={false}
            animate={{
              top: isOpen ? '7px' : '0px',
              rotate: isOpen ? 45 : 0,
            }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          />
          {/* Middle bar */}
          <motion.span
            className="absolute left-0 top-[7px] w-5 h-0.5 bg-current rounded-full"
            initial={false}
            animate={{
              opacity: isOpen ? 0 : 1,
              scaleX: isOpen ? 0 : 1,
            }}
            transition={{ duration: 0.2 }}
          />
          {/* Bottom bar */}
          <motion.span
            className="absolute left-0 w-5 h-0.5 bg-current rounded-full"
            initial={false}
            animate={{
              top: isOpen ? '7px' : '14px',
              rotate: isOpen ? -45 : 0,
            }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          />
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              onClick={() => setIsOpen(false)}
              aria-hidden="true"
            />

            {/* Slide-out Menu */}
            <motion.nav
              ref={navRef}
              className="fixed top-0 right-0 bottom-0 w-72 bg-white z-50 shadow-2xl flex flex-col"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-100">
                <span className="text-lg font-serif text-leaf-700">Menu</span>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
                  aria-label="Close menu"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Navigation Links */}
              <div className="flex-1 py-6">
                {navItems.map((item, index) => (
                  <motion.div
                    key={item.href}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + index * 0.05, duration: 0.3 }}
                  >
                    <Link
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center px-6 py-4 text-lg font-medium transition-all ${
                        isActive(item.href)
                          ? 'text-leaf-600 bg-leaf-50 border-r-4 border-leaf-500'
                          : 'text-gray-700 hover:text-leaf-600 hover:bg-gray-50 active:bg-gray-100'
                      }`}
                    >
                      {item.label}
                    </Link>
                  </motion.div>
                ))}
              </div>

              {/* Footer */}
              <motion.div
                className="p-6 border-t border-gray-100"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <p className="text-xs text-gray-400 text-center">
                  The Green Leaf
                </p>
              </motion.div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
