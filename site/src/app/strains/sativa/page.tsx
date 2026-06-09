import StrainsListing from '@/components/StrainsListing'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Sativa Cannabis Strains — Energizing & Uplifting | The Strain Report',
  description: 'Browse sativa cannabis strains. Cerebral, energizing strains best for daytime use, focus, and creativity. Detailed profiles on effects, terpenes, and growing info.',
  openGraph: {
    title: 'Sativa Cannabis Strains | The Strain Report',
    description: 'Cerebral, energizing strains best for daytime use, focus, and creativity.',
    url: `${baseUrl}/strains/sativa`,
    siteName: 'The Strain Report',
    type: 'website',
  },
  alternates: { canonical: `${baseUrl}/strains/sativa` },
}

type SearchParams = { q?: string; page?: string; compare?: string }

export default async function SativaPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const sp = await searchParams
  return (
    <StrainsListing
      lockedType="sativa"
      heroTitle="Sativa Cannabis Strains"
      heroSubtitle="Cerebral, energizing strains best for daytime use, focus, and creativity."
      basePath="/strains/sativa"
      searchParams={sp}
    />
  )
}
