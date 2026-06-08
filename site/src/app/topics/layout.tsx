import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Cannabis Topics & Guides - The Strain Report',
  description: 'Explore comprehensive cannabis guides organized by topic: strains & genetics, growing & cultivation, consumption methods, health & wellness, legal updates, and culture.',
  keywords: 'cannabis topics, cannabis guides, cannabis strains, growing cannabis, CBD wellness, cannabis edibles, cannabis cultivation',
  openGraph: {
    title: 'Cannabis Topics & Guides',
    description: 'Explore comprehensive cannabis guides organized by topic: strains, growing, consumption, health, legal, and culture.',
    url: 'https://thegreenleaf.com/topics',
    siteName: 'The Strain Report',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cannabis Topics & Guides',
    description: 'Explore comprehensive cannabis guides organized by topic.',
  },
  alternates: {
    canonical: 'https://thegreenleaf.com/topics',
  },
}

export default function TopicsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
