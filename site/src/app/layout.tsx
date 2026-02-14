import type { Metadata } from 'next'
import { Inter, Playfair_Display, Cormorant_Garamond } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import Image from 'next/image'
import Script from 'next/script'
import { Suspense } from 'react'
import SearchBar from '@/components/SearchBar'
import MobileNav from '@/components/MobileNav'
import DesktopNav from '@/components/DesktopNav'
import { HeaderProvider } from '@/components/HeaderContext'
import { PostHogProvider, PostHogPageview } from '@/components/PostHogProvider'
import LogoLink from '@/components/LogoVideo'

const inter = Inter({ subsets: ['latin'] })
const playfair = Playfair_Display({ subsets: ['latin'], style: ['normal', 'italic'], weight: ['400', '700'] })
const cormorant = Cormorant_Garamond({ subsets: ['latin'], weight: ['400', '500', '600', '700'] })

export const metadata: Metadata = {
  metadataBase: new URL('https://lawncare.center'),
  title: 'Lawn Care Center - Expert Lawn Care Tips & Guides',
  description: 'Your trusted source for lawn care advice, seasonal tips, and expert guides to achieve the perfect lawn.',
  keywords: 'lawn care, lawn maintenance, grass care, lawn tips, lawn fertilization, lawn aeration, weed control',
  authors: [{ name: 'Lawn Care Center' }],
  openGraph: {
    title: 'Lawn Care Center - Expert Lawn Care Tips & Guides',
    description: 'Your trusted source for lawn care advice, seasonal tips, and expert guides to achieve the perfect lawn.',
    url: 'https://lawncare.center',
    siteName: 'Lawn Care Center',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: 'https://lawncare.center/images/default-lawn-hero.jpg',
        width: 1792,
        height: 1024,
        alt: 'Lawn Care Center - Professional lawn care advice',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Lawn Care Center - Expert Lawn Care Tips & Guides',
    description: 'Your trusted source for lawn care advice, seasonal tips, and expert guides to achieve the perfect lawn.',
    images: ['https://lawncare.center/images/default-lawn-hero.jpg'],
  },
  alternates: {
    canonical: 'https://lawncare.center',
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
    icon: '/favicon.svg',
    apple: '/apple-touch-icon.png',
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
        <link rel="alternate" type="application/rss+xml" title="Lawn Care Center" href="https://lawncare.center/feed.xml" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="search" type="application/opensearchdescription+xml" title="Lawn Care Center" href="/opensearch.xml" />
        <meta name="theme-color" content="#16a34a" />
        {/* Organization Schema - Site-wide structured data for LLMs and search engines */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              '@id': 'https://lawncare.center/#organization',
              name: 'Lawn Care Center',
              url: 'https://lawncare.center',
              logo: {
                '@type': 'ImageObject',
                url: 'https://lawncare.center/images/logo_accent.png',
                width: 200,
                height: 200,
              },
              description: 'Your trusted source for expert lawn care advice, seasonal tips, and professional guides to achieve the perfect lawn.',
              sameAs: [], // TODO: Add social media profile URLs when created (e.g. Twitter, Facebook, YouTube)
              contactPoint: {
                '@type': 'ContactPoint',
                contactType: 'customer service',
                email: 'contact@lawncare.center',
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
              '@id': 'https://lawncare.center/#website',
              url: 'https://lawncare.center',
              name: 'Lawn Care Center',
              description: 'Expert lawn care tips, guides, and seasonal advice',
              publisher: {
                '@id': 'https://lawncare.center/#organization',
              },
              potentialAction: {
                '@type': 'SearchAction',
                target: {
                  '@type': 'EntryPoint',
                  urlTemplate: 'https://lawncare.center/search?q={search_term_string}',
                },
                'query-input': 'required name=search_term_string',
              },
              inLanguage: 'en-US',
            }),
          }}
        />
        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-NFJG86K02H"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-NFJG86K02H');
          `}
        </Script>
      </head>
      <body className={inter.className}>
        <PostHogProvider>
          <Suspense fallback={null}>
            <PostHogPageview />
          </Suspense>
        <div className="min-h-screen flex flex-col bg-gray-50">
          {/* Skip to content link for keyboard/screen reader users */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:bg-grass-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:outline-none"
          >
            Skip to main content
          </a>

          {/* Header */}
          <HeaderProvider>
            <header className="bg-white border-b border-gray-200 shadow-sm print:hidden">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6 md:py-8">
                <nav className="flex items-center justify-between gap-4">
                  <LogoLink className={`${cormorant.className} text-xl sm:text-2xl md:text-4xl lg:text-5xl font-normal tracking-wide hover:opacity-80 transition flex items-center gap-1 sm:gap-2`} />
                  <div className="flex items-center gap-2 md:gap-8">
                    <SearchBar />
                    <DesktopNav />
                    <MobileNav />
                  </div>
                </nav>
              </div>
            </header>
          </HeaderProvider>

          {/* Main Content */}
          <main id="main-content" className="flex-grow bg-gradient-to-b from-white to-gray-50">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-white border-t border-gray-200 relative overflow-hidden print:hidden">
            {/* Background illustration - right side */}
            <div
              className="absolute right-0 bottom-0 w-80 h-64 md:w-96 md:h-80 pointer-events-none"
              style={{
                backgroundImage: 'url(/images/footer-lawn-transparent.png)',
                backgroundSize: 'contain',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right bottom',
              }}
            />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12 relative z-10">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 md:gap-12">
                <div className="col-span-2 md:col-span-1">
                  <h3 className={`${cormorant.className} text-xl sm:text-2xl mb-3 sm:mb-4`}><span className="text-grass-900">Lawn Care</span> <span className="text-amber-600">Center</span></h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    Your trusted source for expert lawn care advice and seasonal maintenance guides.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-grass-900 mb-4 text-sm uppercase tracking-wide">Quick Links</h3>
                  <ul className="space-y-3 text-sm">
                    <li><Link href="/" className="text-gray-600 hover:text-grass-900 transition">Home</Link></li>
                    <li><Link href="/topics" className="text-gray-600 hover:text-grass-900 transition">Topics</Link></li>
                    <li><Link href="/articles" className="text-gray-600 hover:text-grass-900 transition">All Articles</Link></li>
                    <li><Link href="/videos" className="text-gray-600 hover:text-grass-900 transition">Videos</Link></li>
                    <li><Link href="/about" className="text-gray-600 hover:text-grass-900 transition">About</Link></li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-grass-900 mb-4 text-sm uppercase tracking-wide">Seasons</h3>
                  <ul className="space-y-3 text-sm text-gray-600">
                    <li>Spring Lawn Care</li>
                    <li>Summer Maintenance</li>
                    <li>Fall Preparation</li>
                    <li>Winter Protection</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-grass-900 mb-4 text-sm uppercase tracking-wide">Legal</h3>
                  <ul className="space-y-3 text-sm">
                    <li><Link href="/privacy-policy" className="text-gray-600 hover:text-grass-900 transition">Privacy Policy</Link></li>
                    <li><Link href="/terms-of-service" className="text-gray-600 hover:text-grass-900 transition">Terms of Service</Link></li>
                    <li><Link href="/affiliate-disclosure" className="text-gray-600 hover:text-grass-900 transition">Affiliate Disclosure</Link></li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-gray-200 mt-12 pt-8 text-center text-sm text-gray-500">
                © {new Date().getFullYear()} Lawn Care Center. All rights reserved.
              </div>
            </div>
          </footer>
        </div>
        </PostHogProvider>
      </body>
    </html>
  )
}
