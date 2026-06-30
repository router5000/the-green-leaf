import Link from 'next/link'

type StrainCardData = {
  id: string
  name: string
  slug: string
  strain_type: 'indica' | 'sativa' | 'hybrid'
  thc_min: number | null
  thc_max: number | null
  short_description: string | null
  flavors: string[] | null
}

type CompareContext = {
  compareSlug?: string
  basePath: string
  preserveParams: { q?: string; type?: string }
}

type Props = {
  strain: StrainCardData
  terpenePercentage?: number   // when set, renders subtle green percentage pill
  compare?: CompareContext     // when set, renders Compare button block
}

const TYPE_BADGE: Record<string, string> = {
  indica: 'bg-purple-100 text-purple-700',
  sativa: 'bg-green-100 text-green-700',
  hybrid: 'bg-orange-100 text-orange-600',
}

// Top-edge accent so each strain type is recognizable at a glance and the
// card grid reads less like rows of identical white boxes.
const TYPE_ACCENT: Record<string, string> = {
  indica: 'border-t-purple-400',
  sativa: 'border-t-green-500',
  hybrid: 'border-t-orange-400',
}

export default function StrainCard({ strain, terpenePercentage, compare }: Props) {
  const topFlavors = strain.flavors?.slice(0, 2) ?? []
  const thcRange =
    strain.thc_min != null && strain.thc_max != null
      ? `THC ${strain.thc_min}–${strain.thc_max}%`
      : strain.thc_max != null
        ? `THC up to ${strain.thc_max}%`
        : null

  // View Strain href preserves ?compare if a compare flow is active
  const viewHref = compare?.compareSlug
    ? `/strains/${strain.slug}?compare=${encodeURIComponent(compare.compareSlug)}`
    : `/strains/${strain.slug}`

  // Build Compare button state (only when compare context provided)
  let compareBlock: React.ReactNode = null
  if (compare) {
    let label: string
    let classes: string
    let href: string
    let aria: string

    const { compareSlug, basePath, preserveParams } = compare

    if (!compareSlug) {
      const params = new URLSearchParams()
      if (preserveParams.q)    params.set('q', preserveParams.q)
      if (preserveParams.type) params.set('type', preserveParams.type)
      params.set('compare', strain.slug)
      href = `${basePath}?${params.toString()}`
      label = 'Compare'
      classes = 'bg-white border border-gray-200 text-gray-600 hover:border-leaf-300 hover:text-leaf-700'
      aria = `Compare ${strain.name} with another strain`
    } else if (compareSlug === strain.slug) {
      const params = new URLSearchParams()
      if (preserveParams.q)    params.set('q', preserveParams.q)
      if (preserveParams.type) params.set('type', preserveParams.type)
      const qs = params.toString()
      href = qs ? `${basePath}?${qs}` : basePath
      label = '✓ Selected'
      classes = 'bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200'
      aria = `Cancel ${strain.name} selection`
    } else {
      href = `/strains/compare/${compareSlug}-vs-${strain.slug}`
      label = 'Compare with this'
      classes = 'bg-leaf-600 text-white hover:bg-leaf-700'
      aria = `Compare ${compareSlug} with ${strain.name}`
    }

    compareBlock = (
      <Link
        href={href}
        aria-label={aria}
        className={`text-xs font-medium px-3 py-1.5 rounded-full transition-colors no-underline ${classes}`}
      >
        {label}
      </Link>
    )
  }

  return (
    <div
      className={`bg-white rounded-xl border border-t-4 border-gray-200 ${
        TYPE_ACCENT[strain.strain_type] ?? 'border-t-leaf-500'
      } p-6 flex flex-col gap-3 hover:border-[#2D5016]/30 hover:shadow-md hover:-translate-y-0.5 transition-all`}
    >
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

      <div className="flex items-center gap-2 flex-wrap">
        {thcRange && (
          <p className="text-sm text-gray-500 font-medium">{thcRange}</p>
        )}
        {terpenePercentage != null && (
          <span className="text-xs font-medium bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">
            {terpenePercentage.toFixed(2)}%
          </span>
        )}
      </div>

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
        {compareBlock}
      </div>
    </div>
  )
}
