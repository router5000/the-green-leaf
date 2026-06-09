import StrainsListing from '@/components/StrainsListing'
import { getSupabase } from '@/lib/supabase'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'
const PAGE_SIZE = 24

type SearchParams = { q?: string; type?: string; page?: string }

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}): Promise<Metadata> {
  const sp = await searchParams
  const page = Math.max(1, parseInt(sp.page ?? '1', 10) || 1)

  // Build canonical reflecting the current page
  const canonicalParams = new URLSearchParams()
  if (sp.q)    canonicalParams.set('q', sp.q)
  if (sp.type) canonicalParams.set('type', sp.type)
  if (page > 1) canonicalParams.set('page', String(page))
  const qs = canonicalParams.toString()
  const canonical = qs ? `${baseUrl}/strains?${qs}` : `${baseUrl}/strains`

  // Compute total pages for prev/next link headers
  let totalPages = 1
  try {
    const sb = getSupabase()
    let q = sb.from('strains').select('*', { count: 'exact', head: true }).eq('published', true)
    if (sp.q)    q = q.ilike('name', `%${sp.q}%`)
    if (sp.type) q = q.eq('strain_type', sp.type)
    const { count } = await q
    totalPages = Math.max(1, Math.ceil((count ?? 0) / PAGE_SIZE))
  } catch {
    // env unavailable during build
  }

  const otherLinks: Record<string, string> = {}
  if (page > 1) {
    const prevParams = new URLSearchParams(canonicalParams)
    if (page - 1 === 1) prevParams.delete('page')
    else                prevParams.set('page', String(page - 1))
    otherLinks['prev'] = `${baseUrl}/strains${prevParams.toString() ? `?${prevParams.toString()}` : ''}`
  }
  if (page < totalPages) {
    const nextParams = new URLSearchParams(canonicalParams)
    nextParams.set('page', String(page + 1))
    otherLinks['next'] = `${baseUrl}/strains?${nextParams.toString()}`
  }

  return {
    title: 'Strain Database - Cannabis Strains | The Strain Report',
    description: 'Browse our comprehensive cannabis strain database. Find detailed profiles on effects, terpenes, THC/CBD levels, and growing tips for hundreds of strains.',
    openGraph: {
      title: 'Strain Database | The Strain Report',
      description: 'Browse our comprehensive cannabis strain database.',
      url: canonical,
      siteName: 'The Strain Report',
      type: 'website',
      locale: 'en_US',
    },
    twitter: {
      card: 'summary_large_image',
      title: 'Strain Database | The Strain Report',
      description: 'Browse our comprehensive cannabis strain database.',
    },
    alternates: { canonical },
    other: otherLinks,
  }
}

export default async function StrainsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const sp = await searchParams
  return <StrainsListing searchParams={sp} />
}
