import { getSupabase } from '@/lib/supabase'
import Link from 'next/link'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import StrainFilters from '@/components/StrainFilters'

const PAGE_SIZE = 24

type Strain = {
  id: string
  name: string
  slug: string
  strain_type: 'indica' | 'sativa' | 'hybrid'
  thc_min: number | null
  thc_max: number | null
  short_description: string | null
  flavors: string[] | null
}

const TYPE_BADGE: Record<string, string> = {
  indica: 'bg-purple-100 text-purple-700',
  sativa: 'bg-green-100 text-green-700',
  hybrid: 'bg-orange-100 text-orange-600',
}

const TYPE_HERO_COLOR: Record<string, string> = {
  indica: '#A855F7',
  sativa: '#22C55E',
  hybrid: '#F59E0B',
}

type Props = {
  lockedType?: 'indica' | 'sativa' | 'hybrid'
  heroTitle?: string
  heroSubtitle?: string
  basePath?: string
  searchParams: { q?: string; type?: string; page?: string; compare?: string }
}

export default async function StrainsListing({
  lockedType,
  heroTitle = 'Cannabis Strain Database',
  heroSubtitle = 'Detailed profiles on effects, terpenes, genetics, and growing info for 200+ strains.',
  basePath = '/strains',
  searchParams,
}: Props) {
  const page = Math.max(1, parseInt(searchParams.page ?? '1', 10) || 1)
  const activeType = lockedType ?? searchParams.type
  const compareSlug = searchParams.compare
  const from = (page - 1) * PAGE_SIZE
  const to   = from + PAGE_SIZE - 1

  let strains: Strain[] = []
  let totalCount = 0
  let totalAllCount = 0
  let compareName: string | null = null

  try {
    const sb = getSupabase()

    const { count: allCount } = await sb
      .from('strains')
      .select('*', { count: 'exact', head: true })
      .eq('published', true)
    totalAllCount = allCount ?? 0

    let q = sb
      .from('strains')
      .select('id, name, slug, strain_type, thc_min, thc_max, short_description, flavors', { count: 'exact' })
      .eq('published', true)

    if (searchParams.q) q = q.ilike('name', `%${searchParams.q}%`)
    if (activeType)     q = q.eq('strain_type', activeType)

    const { data, count } = await q
      .order('name', { ascending: true })
      .range(from, to)

    strains    = (data as unknown as Strain[]) ?? []
    totalCount = count ?? 0

    // Look up display name for the banner
    if (compareSlug) {
      const { data: nameRow } = await sb
        .from('strains')
        .select('name')
        .eq('slug', compareSlug)
        .single()
      compareName = (nameRow as { name: string } | null)?.name ?? null
    }
  } catch {
    // env unavailable during build
  }

  const totalPages  = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))
  const hasFilters  = !!(searchParams.q || (!lockedType && searchParams.type))
  const showingFrom = totalCount === 0 ? 0 : from + 1
  const showingTo   = Math.min(from + PAGE_SIZE, totalCount)

  const dynamicSubtitle = hasFilters
    ? `Showing ${showingFrom}–${showingTo} of ${totalCount} ${activeType ?? ''} strains`.replace(/\s+/g, ' ').trim()
    : heroSubtitle

  function pageHref(p: number) {
    const params = new URLSearchParams()
    if (searchParams.q)                   params.set('q', searchParams.q)
    if (!lockedType && searchParams.type) params.set('type', searchParams.type)
    if (compareSlug)                      params.set('compare', compareSlug)
    if (p > 1)                            params.set('page', String(p))
    const qs = params.toString()
    return qs ? `${basePath}?${qs}` : basePath
  }

  // Tab suffix preserves ?compare across route switches
  const tabSuffix = compareSlug ? `?compare=${encodeURIComponent(compareSlug)}` : ''

  // Cancel-compare href: current path with all other params, just no `compare`
  function cancelCompareHref() {
    const params = new URLSearchParams()
    if (searchParams.q)                   params.set('q', searchParams.q)
    if (!lockedType && searchParams.type) params.set('type', searchParams.type)
    if (page > 1)                         params.set('page', String(page))
    const qs = params.toString()
    return qs ? `${basePath}?${qs}` : basePath
  }

  const heroColor = lockedType ? TYPE_HERO_COLOR[lockedType] : '#F59E0B'

  const tabs = [
    { label: 'All Strains', href: `/strains${tabSuffix}`,        match: undefined },
    { label: 'Indica',      href: `/strains/indica${tabSuffix}`, match: 'indica'  },
    { label: 'Sativa',      href: `/strains/sativa${tabSuffix}`, match: 'sativa'  },
    { label: 'Hybrid',      href: `/strains/hybrid${tabSuffix}`, match: 'hybrid'  },
  ] as const

  return (
    <div className="bg-[#f0f0f0]">
      {/* Top separator */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* Hero */}
      <div className="relative py-16 overflow-hidden">
        <BlinkingSquares
          className="absolute inset-0"
          width="100%"
          height="100%"
          direction="right"
          gridSize={52}
          squareColor={heroColor}
          backgroundColor="#f0f0f0"
          falloff={1.25}
          fadeStart={0.33}
          fadeEnd={1}
          squareSize={0.57}
          minBrightness={0.55}
          twinkleSpeed={1.4}
          twinkleStrength={0.94}
          intensity={1}
          opacity={0.4}
          dpr={1.5}
        />
        <div className="relative z-10 max-w-6xl mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#1a3a0a' }}>
            {heroTitle}
          </h1>
          <p className="text-xl max-w-2xl mb-4" style={{ color: '#2d4a1e' }}>
            {dynamicSubtitle}
          </p>
          <span
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/70 backdrop-blur-sm text-sm font-medium border border-amber-300/40"
            style={{ color: '#2d4a1e' }}
          >
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            {totalAllCount} {totalAllCount === 1 ? 'strain' : 'strains'} in the database
          </span>
        </div>
      </div>

      {/* Bottom separator */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      <div className="px-4 sm:px-6 md:px-[160px] py-12">
        {/* Compare banner */}
        {compareSlug && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mb-6 flex items-center justify-between gap-3 flex-wrap">
            <p className="text-sm text-amber-900">
              <span className="font-semibold">Comparing {compareName ?? compareSlug}</span> — now pick a second strain to compare.
            </p>
            <Link
              href={cancelCompareHref()}
              className="text-sm font-medium text-amber-700 hover:text-amber-900 no-underline"
            >
              Cancel
            </Link>
          </div>
        )}

        {/* Type tabs */}
        <nav className="flex flex-wrap gap-2 mb-6" aria-label="Strain type">
          {tabs.map((t) => {
            const active = t.match === lockedType
            return (
              <Link
                key={t.href}
                href={t.href}
                className={`px-5 py-2 rounded-full text-sm font-medium transition-colors no-underline ${
                  active
                    ? 'bg-leaf-700 text-white'
                    : 'bg-white border border-gray-200 text-gray-700 hover:border-leaf-300 hover:text-leaf-700'
                }`}
                aria-current={active ? 'page' : undefined}
              >
                {t.label}
              </Link>
            )
          })}
        </nav>

        {/* Filters */}
        <StrainFilters />

        {strains.length === 0 ? (
          <p className="text-gray-500 text-center py-16">
            No strains match your filters.{' '}
            <Link href={basePath} className="text-leaf-600 hover:text-leaf-700 underline">
              Clear filters
            </Link>
          </p>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {strains.map((strain) => (
                <StrainCard
                  key={strain.id}
                  strain={strain}
                  basePath={basePath}
                  compareSlug={compareSlug}
                  preserveParams={{
                    q:    searchParams.q,
                    type: !lockedType ? searchParams.type : undefined,
                  }}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-12 pt-6 border-t border-gray-200 flex-wrap gap-4">
                <p className="text-sm text-gray-500">
                  Showing {showingFrom}–{showingTo} of {totalCount} strains
                </p>
                <div className="flex gap-2 items-center">
                  {page > 1 && (
                    <Link
                      href={pageHref(page - 1)}
                      className="px-4 py-2 rounded-full text-sm font-medium bg-white border border-gray-200 text-gray-700 hover:bg-leaf-50 hover:border-leaf-300 transition-colors no-underline"
                    >
                      ← Previous
                    </Link>
                  )}
                  <span className="px-4 py-2 text-sm font-medium text-gray-500">
                    Page {page} of {totalPages}
                  </span>
                  {page < totalPages && (
                    <Link
                      href={pageHref(page + 1)}
                      className="px-4 py-2 rounded-full text-sm font-medium bg-leaf-600 text-white hover:bg-leaf-700 transition-colors no-underline"
                    >
                      Next →
                    </Link>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

function StrainCard({
  strain,
  basePath,
  compareSlug,
  preserveParams,
}: {
  strain: Strain
  basePath: string
  compareSlug?: string
  preserveParams: { q?: string; type?: string }
}) {
  const topFlavors = strain.flavors?.slice(0, 2) ?? []
  const thcRange =
    strain.thc_min != null && strain.thc_max != null
      ? `THC ${strain.thc_min}–${strain.thc_max}%`
      : strain.thc_max != null
        ? `THC up to ${strain.thc_max}%`
        : null

  // Build hrefs that preserve compare state across navigation
  function hrefWithCompare(base: string, withCompare: string | null) {
    const params = new URLSearchParams()
    if (withCompare) params.set('compare', withCompare)
    const qs = params.toString()
    return qs ? `${base}?${qs}` : base
  }

  // View Strain link preserves ?compare so the user keeps their selection
  const viewHref = hrefWithCompare(`/strains/${strain.slug}`, compareSlug ?? null)

  // Compare button has three states
  let compareLabel: string
  let compareClasses: string
  let compareHref: string
  let compareAriaLabel: string

  if (!compareSlug) {
    // Start a new comparison — set ?compare on the current listing path
    const params = new URLSearchParams()
    if (preserveParams.q)    params.set('q', preserveParams.q)
    if (preserveParams.type) params.set('type', preserveParams.type)
    params.set('compare', strain.slug)
    compareHref = `${basePath}?${params.toString()}`
    compareLabel = 'Compare'
    compareClasses = 'bg-white border border-gray-200 text-gray-600 hover:border-leaf-300 hover:text-leaf-700'
    compareAriaLabel = `Compare ${strain.name} with another strain`
  } else if (compareSlug === strain.slug) {
    // This strain is already selected — clicking cancels selection
    const params = new URLSearchParams()
    if (preserveParams.q)    params.set('q', preserveParams.q)
    if (preserveParams.type) params.set('type', preserveParams.type)
    const qs = params.toString()
    compareHref = qs ? `${basePath}?${qs}` : basePath
    compareLabel = '✓ Selected'
    compareClasses = 'bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200'
    compareAriaLabel = `Cancel ${strain.name} selection`
  } else {
    // Other strain selected — go straight to comparison
    compareHref = `/strains/compare/${compareSlug}-vs-${strain.slug}`
    compareLabel = 'Compare with this'
    compareClasses = 'bg-leaf-600 text-white hover:bg-leaf-700'
    compareAriaLabel = `Compare ${compareSlug} with ${strain.name}`
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 flex flex-col gap-3 hover:border-[#2D5016]/30 hover:shadow-sm transition-all">
      <div className="flex items-start justify-between gap-2">
        <h2 className="font-serif text-xl text-gray-900 leading-tight">{strain.name}</h2>
        <span
          className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full capitalize ${
            TYPE_BADGE[strain.strain_type] ?? 'bg-gray-100 text-gray-600'
          }`}
        >
          {strain.strain_type}
        </span>
      </div>

      {thcRange && (
        <p className="text-sm text-gray-500 font-medium">{thcRange}</p>
      )}

      {strain.short_description && (
        <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">{strain.short_description}</p>
      )}

      {topFlavors.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {topFlavors.map((f) => (
            <span key={f} className="text-xs bg-gray-100 text-gray-500 px-2.5 py-1 rounded-full capitalize">
              {f}
            </span>
          ))}
        </div>
      )}

      <div className="mt-auto pt-2 flex items-center justify-between gap-2">
        <Link
          href={viewHref}
          className="text-sm font-medium text-[#2D5016] hover:text-[#3a6b1e] no-underline inline-flex items-center gap-1 transition-colors"
        >
          View Strain <span aria-hidden="true">→</span>
        </Link>
        <Link
          href={compareHref}
          aria-label={compareAriaLabel}
          className={`text-xs font-medium px-3 py-1.5 rounded-full transition-colors no-underline ${compareClasses}`}
        >
          {compareLabel}
        </Link>
      </div>
    </div>
  )
}
