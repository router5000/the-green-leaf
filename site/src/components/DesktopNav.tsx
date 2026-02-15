'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/topics', label: 'Topics' },
  { href: '/articles', label: 'Articles' },
  { href: '/videos', label: 'Videos' },
]

export default function DesktopNav() {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname === href || pathname.startsWith(`${href}/`)
  }

  return (
    <div className="hidden sm:flex items-center space-x-8 text-sm uppercase tracking-wide">
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`transition ${
            isActive(item.href)
              ? 'text-leaf-700 font-semibold border-b-2 border-leaf-500 pb-0.5'
              : 'text-gray-600 hover:text-leaf-900'
          }`}
        >
          {item.label}
        </Link>
      ))}
    </div>
  )
}
