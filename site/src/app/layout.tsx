import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { GoogleAnalytics } from '@next/third-parties/google'
import { HeaderProvider } from '@/components/HeaderContext'
import SiteNav from '@/components/SiteNav'
import Footer7 from '@/components/ui/Footer7'
import { Analytics } from '@vercel/analytics/next'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL('https://strainreport.com'),
  title: 'The Strain Report - Cannabis Education, Guides & News',
  description: 'Your trusted source for cannabis education — strain guides, growing tips, health & wellness, and industry news.',
  keywords: 'cannabis, marijuana, strains, growing cannabis, CBD, edibles, cannabis health, legalization',
  authors: [{ name: 'The Strain Report' }],
  openGraph: {
    title: 'The Strain Report - Cannabis Education, Guides & News',
    description: 'Your trusted source for cannabis education — strain guides, growing tips, health & wellness, and industry news.',
    url: 'https://strainreport.com',
    siteName: 'The Strain Report',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: 'https://strainreport.com/images/default-leaf-hero.jpg',
        width: 1792,
        height: 1024,
        alt: 'The Strain Report - Cannabis education and guides',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'The Strain Report - Cannabis Education, Guides & News',
    description: 'Your trusted source for cannabis education — strain guides, growing tips, health & wellness, and industry news.',
    images: ['https://strainreport.com/images/default-leaf-hero.jpg'],
  },
  alternates: {
    canonical: 'https://strainreport.com',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
    shortcut: '/favicon.ico',
    apple: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="alternate" type="application/rss+xml" title="The Strain Report" href="https://strainreport.com/feed.xml" />
        <link rel="manifest" href="/manifest.json" />
        {/* Vercel Web Analytics — script tag in SSR HTML (HUSA-75).
            <Analytics /> from @vercel/analytics/next injects via JS post-hydration,
            which doesn't satisfy the apex-curl verification. */}
        <script defer src="/_vercel/insights/script.js" />
        <link rel="search" type="application/opensearchdescription+xml" title="The Strain Report" href="/opensearch.xml" />
        <meta name="theme-color" content="#2D5016" />
        {/* Organization Schema - Site-wide structured data for LLMs and search engines */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              '@id': 'https://strainreport.com/#organization',
              name: 'The Strain Report',
              url: 'https://strainreport.com',
              logo: {
                '@type': 'ImageObject',
                url: 'https://strainreport.com/images/logo_accent.png',
                width: 200,
                height: 200,
              },
              description: 'Your trusted source for cannabis education — strain guides, growing tips, health & wellness, and industry news.',
              sameAs: [],
              contactPoint: {
                '@type': 'ContactPoint',
                contactType: 'customer service',
                email: 'contact@strainreport.com',
              },
            }),
          }}
        />
        {/* WebSite Schema for sitelinks search */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebSite',
              '@id': 'https://strainreport.com/#website',
              url: 'https://strainreport.com',
              name: 'The Strain Report',
              description: 'Cannabis education, strain guides, growing tips, and industry news',
              publisher: {
                '@id': 'https://strainreport.com/#organization',
              },
              potentialAction: {
                '@type': 'SearchAction',
                target: {
                  '@type': 'EntryPoint',
                  urlTemplate: 'https://strainreport.com/search?q={search_term_string}',
                },
                'query-input': 'required name=search_term_string',
              },
              inLanguage: 'en-US',
            }),
          }}
        />
      </head>
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col bg-[#f0f0f0]">
            {/* Skip to content link for keyboard/screen reader users */}
            <a
              href="#main-content"
              className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:bg-leaf-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:outline-none"
            >
              Skip to main content
            </a>

            {/* Navigation */}
            <HeaderProvider>
              <SiteNav />
            </HeaderProvider>

            {/* Main Content — offset below fixed top nav */}
            <main id="main-content" className="flex-grow bg-[#f0f0f0] pt-16">
              {children}
            </main>

            {/* Footer */}
            <Footer7 />
        </div>
        <Analytics />
        {process.env.NODE_ENV === 'production' && <GoogleAnalytics gaId="G-THX1437Q8P" />}
      </body>
    </html>
  )
}
