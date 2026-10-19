'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useEffect, useState, useTransition } from 'react'
import { CompareAwareLink } from '@/components/CompareNav'

export default function StrainFilters() {
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

  const hasSearch = !!params.get('q')

  // Preserve ?compare across clear-search
  const clearHref = pathname

  return (
    <div className="flex flex-col gap-4 mb-8">
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search strains by name…"
        aria-label="Search strains"
        className="w-full px-4 py-3 rounded-full border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-leaf-500 focus:border-transparent"
      />

      {hasSearch && (
        <div>
          <CompareAwareLink
            href={clearHref}
            compareSlug={params.get('compare') ?? undefined}
            className="text-sm font-medium text-gray-500 hover:text-leaf-700 transition-colors"
          >
            Clear search
          </CompareAwareLink>
        </div>
      )}
    </div>
  )
}
