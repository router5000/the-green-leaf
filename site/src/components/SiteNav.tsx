'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'motion/react'
import { Menu, X } from 'lucide-react'
import SearchBar from '@/components/SearchBar'
import LogoVideo from '@/components/LogoVideo'

const navItems = [
  { label: 'Home',     href: '/' },
  { label: 'Topics',   href: '/topics' },
  { label: 'Articles', href: '/articles' },
  { label: 'Videos',   href: '/videos' },
]

export default function SiteNav() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname === href || pathname.startsWith(`${href}/`)
  }

  return (
    <>
      {/* ── Fixed top bar ───────────────────────────────────────────── */}
      <motion.header
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
        className="fixed top-0 left-0 right-0 z-50 h-16 print:hidden bg-[#f0f0f0]"
      >
        {/* Three-column grid: logo | centered nav | right actions */}
        <div className="h-full px-4 sm:px-6 md:px-[160px] grid grid-cols-3 items-center">

          {/* Col 1 — Logo left */}
          <motion.div
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="flex items-center"
          >
            <LogoVideo
              className="flex items-center gap-2 no-underline text-base font-semibold"
            />
          </motion.div>

          {/* Col 2 — Nav links absolutely centered */}
          <nav
            className="hidden md:flex items-center justify-center gap-1"
            aria-label="Main navigation"
          >
            {navItems.map((item, i) => {
              const active = isActive(item.href)
              return (
                <motion.div
                  key={item.href}
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.15 + i * 0.07 }}
                  className="relative"
                >
                  <Link
                    href={item.href}
                    className={`relative flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors no-underline ${
                      active
                        ? 'text-[#2D5016]'
                        : 'text-gray-600 hover:text-[#2D5016] hover:bg-leaf-50'
                    }`}
                    aria-current={active ? 'page' : undefined}
                  >
                    {item.label}
                    {active && (
                      <motion.span
                        layoutId="nav-active-pill"
                        className="absolute bottom-0.5 left-3 right-3 h-0.5 rounded-full bg-[#2D5016]"
                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                      />
                    )}
                  </Link>
                </motion.div>
              )
            })}
          </nav>

          {/* Col 3 — Search + mobile toggle, right-aligned */}
          <motion.div
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="flex items-center justify-end gap-2"
          >
            <SearchBar />

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden flex items-center justify-center w-9 h-9 rounded-lg text-gray-600 hover:text-[#2D5016] hover:bg-leaf-50 transition-colors"
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </motion.div>

        </div>
      </motion.header>

      {/* ── Mobile dropdown ──────────────────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="md:hidden fixed inset-0 top-16 bg-black/20 backdrop-blur-sm z-40"
              onClick={() => setMobileOpen(false)}
              aria-hidden="true"
            />

            <motion.nav
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
              className="md:hidden fixed top-16 left-0 right-0 z-50 bg-[#f0f0f0] border-b border-[#e5e5e5] shadow-xl"
              aria-label="Mobile navigation"
            >
              <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-1">
                {navItems.map((item) => {
                  const active = isActive(item.href)
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className={`px-4 py-3 rounded-lg text-sm font-medium no-underline transition-colors ${
                        active
                          ? 'bg-leaf-50 text-[#2D5016] font-semibold'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-[#2D5016]'
                      }`}
                      aria-current={active ? 'page' : undefined}
                    >
                      {item.label}
                    </Link>
                  )
                })}
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
