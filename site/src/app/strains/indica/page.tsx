import StrainsListing from '@/components/StrainsListing'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Indica Cannabis Strains — Relaxing & Sedating | The Strain Report',
  description: 'Browse indica cannabis strains. Body-focused, calming strains best for evening use, deep relaxation, and sleep. Detailed profiles on effects, terpenes, and growing info.',
  openGraph: {
    title: 'Indica Cannabis Strains | The Strain Report',
    description: 'Body-focused, calming strains best for evening use, deep relaxation, and sleep.',
    url: `${baseUrl}/strains/indica`,
    siteName: 'The Strain Report',
    type: 'website',
  },
  alternates: { canonical: `${baseUrl}/strains/indica` },
}

type SearchParams = { q?: string; page?: string }

export default async function IndicaPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const sp = await searchParams
  return (
    <StrainsListing
      lockedType="indica"
      heroTitle="Indica Cannabis Strains"
      heroSubtitle="Body-focused, calming strains best for evening use, deep relaxation, and sleep."
      basePath="/strains/indica"
      searchParams={sp}
    />
  )
}
