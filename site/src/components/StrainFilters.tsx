'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useEffect, useState, useTransition } from 'react'
import Link from 'next/link'

const TYPE_OPTIONS = ['all', 'indica', 'sativa', 'hybrid'] as const
const DIFFICULTY_OPTIONS = ['all', 'easy', 'moderate', 'difficult'] as const
const SORT_OPTIONS = [
  { value: 'name_asc',  label: 'A–Z' },
  { value: 'name_desc', label: 'Z–A' },
  { value: 'thc_desc',  label: 'THC: High–Low' },
  { value: 'thc_asc',   label: 'THC: Low–High' },
] as const

export default function StrainFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const params = useSearchParams()
  const [, startTransition] = useTransition()

  const [search, setSearch] = useState(params.get('q') ?? '')

  // Keep input in sync if URL changes externally (e.g. Clear filters link)
  useEffect(() => {
    setSearch(params.get('q') ?? '')
  }, [params])

  // Debounce search → URL
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

  const activeType       = params.get('type')       ?? 'all'
  const activeDifficulty = params.get('difficulty') ?? 'all'
  const activeSort       = params.get('sort')       ?? 'name_asc'
  const hasFilters       = !!(params.get('q') || params.get('type') || params.get('difficulty')
                            || params.get('thc_min') || params.get('thc_max')
                            || (params.get('sort') && params.get('sort') !== 'name_asc'))

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

      {/* Type pills */}
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

      {/* Difficulty pills */}
      <div className="flex flex-wrap gap-2">
        {DIFFICULTY_OPTIONS.map((d) => (
          <button
            key={d}
            type="button"
            onClick={() => pushParam('difficulty', d === 'all' ? null : d)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors capitalize ${
              activeDifficulty === d
                ? 'bg-leaf-600 text-white'
                : 'bg-leaf-100 text-leaf-700 hover:bg-leaf-200'
            }`}
          >
            {d === 'all' ? 'All difficulty' : d}
          </button>
        ))}
      </div>

      {/* Sort + Clear */}
      <div className="flex items-center gap-3 flex-wrap">
        <select
          value={activeSort}
          onChange={(e) => pushParam('sort', e.target.value === 'name_asc' ? null : e.target.value)}
          aria-label="Sort strains"
          className="px-4 py-2 rounded-full border border-gray-200 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-leaf-500"
        >
          {SORT_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>Sort: {s.label}</option>
          ))}
        </select>

        {hasFilters && (
          <Link
            href={pathname}
            className="text-sm font-medium text-gray-500 hover:text-leaf-700 transition-colors"
          >
            Clear filters
          </Link>
        )}
      </div>
    </div>
  )
}
