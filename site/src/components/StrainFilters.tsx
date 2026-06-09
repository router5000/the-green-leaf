'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useEffect, useState, useTransition } from 'react'
import Link from 'next/link'

const TYPE_OPTIONS = ['all', 'indica', 'sativa', 'hybrid'] as const

type Props = {
  lockedType?: 'indica' | 'sativa' | 'hybrid'
}

export default function StrainFilters({ lockedType }: Props) {
  const router = useRouter()
  const pathname = usePathname()
  const params = useSearchParams()
  const [, startTransition] = useTransition()

  const [search, setSearch] = useState(params.get('q') ?? '')

  useEffect(() => {
    setSearch(params.get('q') ?? '')
  }, [params])

  useEffect(() => {
    const current = params.get('q') ?? ''
    if (search === current) return
    const t = setTimeout(() => {
      pushParam('q', search || null)
    }, 300)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search])

  function pushParam(key: string, value: string | null) {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else       next.delete(key)
    if (key !== 'page') next.delete('page')
    const qs = next.toString()
    startTransition(() => {
      router.push(qs ? `${pathname}?${qs}` : pathname, { scroll: false })
    })
  }

  const activeType = lockedType ?? (params.get('type') ?? 'all')
  const hasFilters = !!(params.get('q') || (!lockedType && params.get('type')))

  return (
    <div className="flex flex-col gap-4 mb-8">
      {/* Search */}
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search strains by name…"
        aria-label="Search strains"
        className="w-full px-4 py-3 rounded-full border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-leaf-500 focus:border-transparent"
      />

      {/* Type pills — hidden on type landing pages */}
      {!lockedType && (
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex flex-wrap gap-2">
            {TYPE_OPTIONS.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => pushParam('type', t === 'all' ? null : t)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors capitalize ${
                  activeType === t
                    ? 'bg-leaf-600 text-white'
                    : 'bg-leaf-100 text-leaf-700 hover:bg-leaf-200'
                }`}
              >
                {t === 'all' ? 'All types' : t}
              </button>
            ))}
          </div>

          {hasFilters && (
            <Link
              href={pathname}
              className="text-sm font-medium text-gray-500 hover:text-leaf-700 transition-colors"
            >
              Clear filters
            </Link>
          )}
        </div>
      )}

      {/* On locked pages, only show clear if search is set */}
      {lockedType && hasFilters && (
        <div>
          <Link
            href={pathname}
            className="text-sm font-medium text-gray-500 hover:text-leaf-700 transition-colors"
          >
            Clear search
          </Link>
        </div>
      )}
    </div>
  )
}
