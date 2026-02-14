import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Lawn Care Topics & Guides - Lawn Care Center',
  description: 'Explore comprehensive lawn care guides organized by topic: seasonal care, weed control, lawn health, equipment, and more. Expert advice for a beautiful lawn.',
  keywords: 'lawn care topics, lawn care guides, seasonal lawn care, weed control, lawn maintenance, grass care, lawn equipment',
  openGraph: {
    title: 'Lawn Care Topics & Guides',
    description: 'Explore comprehensive lawn care guides organized by topic: seasonal care, weed control, lawn health, equipment, and more.',
    url: 'https://lawncare.center/topics',
    siteName: 'Lawn Care Center',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Lawn Care Topics & Guides',
    description: 'Explore comprehensive lawn care guides organized by topic.',
  },
  alternates: {
    canonical: 'https://lawncare.center/topics',
  },
}

export default function TopicsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
