import { statesData } from '@/data/statesData'
import StatesClient from './StatesClient'
import type { Metadata } from 'next'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Cannabis Laws by State - Possession Limits & Legality | The Strain Report',
  description: 'Current cannabis laws, possession limits, home-grow rules, and legal status for all 50 US states — updated for 2025.',
  openGraph: {
    title: 'Cannabis Laws by State - The Strain Report',
    description: 'Current cannabis laws, possession limits, and legal status for all 50 US states.',
    url: `${baseUrl}/states`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cannabis Laws by State - The Strain Report',
    description: 'Possession limits, home-grow rules, and legal status for all 50 US states.',
  },
  alternates: {
    canonical: `${baseUrl}/states`,
  },
}

export default function StatesPage() {
  return <StatesClient states={statesData} />
}
