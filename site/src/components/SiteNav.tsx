'use client'

import { useState, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  AnimatePresence,
} from 'motion/react'
import { Home, BookOpen, FileText, Play, Menu, X } from 'lucide-react'
import SearchBar from '@/components/SearchBar'

const navItems = [
  { id: 'home',     icon: Home,     label: 'Home',     href: '/' },
  { id: 'topics',   icon: BookOpen,  label: 'Topics',   href: '/topics' },
  { id: 'articles', icon: FileText,  label: 'Articles', href: '/articles' },
  { id: 'videos',   icon: Play,      label: 'Videos',   href: '/videos' },
]

// ─── Desktop dock item ────────────────────────────────────────────────────────

interface NavItemProps {
  item: (typeof navItems)[number]
  index: number
  mouseY: ReturnType<typeof useMotionValue<number>>
  hoveredItem: string | null
  setHoveredItem: (id: string | null) => void
  isActive: boolean
}

function NavItem({ item, index, mouseY, hoveredItem, setHoveredItem, isActive }: NavItemProps) {
  const ref = useRef<HTMLDivElement>(null)
  const Icon = item.icon

  const distance = useTransform(mouseY, (val: number) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { y: 0, height: 0 }
    return val - bounds.y - bounds.height / 2
  })

  const sizeTransform = useTransform(distance, [-150, -75, 0, 75, 150], [48, 54, 62, 54, 48])
  const size = useSpring(sizeTransform, { mass: 0.1, stiffness: 150, damping: 12 })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.3 + index * 0.1, ease: [0.4, 0, 0.2, 1] }}
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
      onMouseEnter={() => setHoveredItem(item.id)}
      onMouseLeave={() => setHoveredItem(null)}
    >
      <Link
        href={item.href}
        className={`flex items-center justify-center w-full h-full rounded-2xl no-underline transition-colors ${
          isActive
            ? 'bg-leaf-600 text-white shadow-md'
            : 'bg-leaf-50 text-leaf-700 hover:bg-leaf-100'
        }`}
        aria-label={item.label}
        aria-current={isActive ? 'page' : undefined}
      >
        <Icon className="w-5 h-5" />
      </Link>

      <AnimatePresence>
        {hoveredItem === item.id && (
          <motion.div
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -8 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute left-full ml-3 top-1/2 -translate-y-1/2 whitespace-nowrap px-3 py-1.5 rounded-lg bg-leaf-600 text-white text-sm font-medium shadow-lg pointer-events-none z-10"
          >
            {item.label}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// ─── Mobile dock item ─────────────────────────────────────────────────────────

interface MobileNavItemProps {
  item: (typeof navItems)[number]
  index: number
  isActive: boolean
  onSelect: () => void
}

function MobileNavItem({ item, index, isActive, onSelect }: MobileNavItemProps) {
  const Icon = item.icon

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.25, delay: 0.05 + index * 0.07, ease: [0.4, 0, 0.2, 1] }}
      className="flex flex-col items-center gap-1"
    >
      <Link
        href={item.href}
        onClick={onSelect}
        className={`flex items-center justify-center w-12 h-12 rounded-2xl no-underline transition-colors ${
          isActive
            ? 'bg-leaf-600 text-white shadow-md'
            : 'bg-leaf-50 text-leaf-700 hover:bg-leaf-100'
        }`}
        aria-label={item.label}
        aria-current={isActive ? 'page' : undefined}
      >
        <Icon className="w-5 h-5" />
      </Link>
      <span className={`text-xs font-medium ${isActive ? 'text-leaf-600' : 'text-gray-500'}`}>
        {item.label}
      </span>
    </motion.div>
  )
}

// ─── Main export ──────────────────────────────────────────────────────────────

export default function SiteNav() {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()
  const mouseY = useMotionValue<number>(Infinity)

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname === href || pathname.startsWith(`${href}/`)
  }

  return (
    <>
      {/* ── Mobile: fixed top bar ─────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
        className="md:hidden fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 px-4 py-3 print:hidden"
      >
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 no-underline">
            <div className="w-8 h-8 rounded-full bg-leaf-600" />
            <span className="font-serif text-base text-leaf-900 font-medium">The Green Leaf</span>
          </Link>
          <div className="flex items-center gap-2">
            <SearchBar />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="flex h-9 w-9 items-center justify-center rounded-md bg-leaf-600 text-white"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </motion.div>

      {/* ── Mobile: bottom dock ───────────────────────────────────────────── */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              onClick={() => setMobileMenuOpen(false)}
              aria-hidden="true"
            />
            <motion.nav
              initial={{ opacity: 0, y: 80 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 80 }}
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
              className="md:hidden fixed bottom-6 left-0 right-0 z-50 px-4"
              aria-label="Main navigation"
            >
              <div className="flex items-end justify-center gap-5 px-6 py-4 rounded-3xl bg-white/95 backdrop-blur-2xl border border-gray-200 shadow-2xl mx-auto w-fit">
                {navItems.map((item, index) => (
                  <MobileNavItem
                    key={item.id}
                    item={item}
                    index={index}
                    isActive={isActive(item.href)}
                    onSelect={() => setMobileMenuOpen(false)}
                  />
                ))}
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>

      {/* ── Desktop: fixed left sidebar ───────────────────────────────────── */}
      <motion.nav
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="hidden md:flex fixed left-0 top-0 h-screen w-24 flex-col items-center py-8 bg-white border-r border-gray-100 shadow-sm z-50 print:hidden"
        aria-label="Main navigation"
      >
        {/* Logo circle */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.4, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
          className="mb-10"
        >
          <Link href="/" aria-label="The Green Leaf — Home">
            <div className="w-10 h-10 rounded-full bg-leaf-600 hover:opacity-80 transition-opacity" />
          </Link>
        </motion.div>

        {/* Dock nav items with magnetic scaling */}
        <motion.div
          className="flex-1 flex flex-col items-center justify-center gap-3"
          onMouseMove={(e) => mouseY.set(e.pageY)}
          onMouseLeave={() => mouseY.set(Infinity)}
        >
          {navItems.map((item, index) => (
            <NavItem
              key={item.id}
              item={item}
              index={index}
              mouseY={mouseY}
              hoveredItem={hoveredItem}
              setHoveredItem={setHoveredItem}
              isActive={isActive(item.href)}
            />
          ))}
        </motion.div>

        {/* Brand text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.8 }}
          className="text-center mt-6"
        >
          <p className="text-xs font-semibold text-leaf-900 leading-tight">The Green</p>
          <p className="text-xs font-semibold text-amber-600 leading-tight">Leaf</p>
        </motion.div>
      </motion.nav>
    </>
  )
}
