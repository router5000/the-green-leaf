import StrainsListing from '@/components/StrainsListing'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Hybrid Cannabis Strains — Balanced Effects | The Strain Report',
  description: 'Browse hybrid cannabis strains. Balanced strains combining indica and sativa effects for versatile use. Detailed profiles on effects, terpenes, and growing info.',
  openGraph: {
    title: 'Hybrid Cannabis Strains | The Strain Report',
    description: 'Balanced strains combining indica and sativa effects for versatile use.',
    url: `${baseUrl}/strains/hybrid`,
    siteName: 'The Strain Report',
    type: 'website',
  },
  alternates: { canonical: `${baseUrl}/strains/hybrid` },
}

type SearchParams = { q?: string; page?: string }

export default async function HybridPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const sp = await searchParams
  return (
    <StrainsListing
      lockedType="hybrid"
      heroTitle="Hybrid Cannabis Strains"
      heroSubtitle="Balanced strains combining indica and sativa effects for versatile use."
      basePath="/strains/hybrid"
      searchParams={sp}
    />
  )
}
