'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

/**
 * Compare-flow navigation that never emits a crawlable `?compare=` href.
 * Crawlers see either a <button> or a plain <a href={href}>; the compare
 * state is only added on click, client-side.
 */

/** Link whose crawlable href is clean; on click, `?compare=` is carried over. */
export function CompareAwareLink({
  href,
  compareSlug,
  className,
  children,
  ...rest
}: {
  href: string
  compareSlug?: string
  className?: string
  children: React.ReactNode
} & Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'onClick'>) {
  const router = useRouter()
  return (
    <a
      href={href}
      className={className}
      onClick={(e) => {
        if (!compareSlug || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return
        e.preventDefault()
        const url = new URL(href, window.location.origin)
        url.searchParams.set('compare', compareSlug)
        router.push(`${url.pathname}?${url.searchParams.toString()}`)
      }}
      {...rest}
    >
      {children}
    </a>
  )
}

/** Button that navigates to a compare-state URL on click (no href). */
export function CompareButton({
  to,
  className,
  ariaLabel,
  children,
}: {
  to: string
  className?: string
  ariaLabel?: string
  children: React.ReactNode
}) {
  const router = useRouter()
  return (
    <button type="button" aria-label={ariaLabel} className={className} onClick={() => router.push(to)}>
      {children}
    </button>
  )
}

const STRAIN_COMPARE_CLASS =
  'inline-flex items-center gap-2 px-4 py-2 rounded-full bg-leaf-600 text-white text-sm font-medium hover:bg-leaf-700 transition-colors cursor-pointer'

function StrainCompareInner({ slug }: { slug: string }) {
  const sp = useSearchParams()
  const other = sp.get('compare')
  const active = other && other !== slug
  return (
    <CompareButton
      to={active ? `/strains/compare/${other}-vs-${slug}` : `/strains?compare=${slug}`}
      className={STRAIN_COMPARE_CLASS}
    >
      {active ? `Compare with ${other} →` : 'Compare with another strain →'}
    </CompareButton>
  )
}

/** Compare button on a strain profile; reads ?compare client-side so the
 *  profile itself can be statically rendered. */
export function StrainCompareButton({ slug }: { slug: string }) {
  return (
    <Suspense
      fallback={
        <CompareButton to={`/strains?compare=${slug}`} className={STRAIN_COMPARE_CLASS}>
          Compare with another strain →
        </CompareButton>
      }
    >
      <StrainCompareInner slug={slug} />
    </Suspense>
  )
}
