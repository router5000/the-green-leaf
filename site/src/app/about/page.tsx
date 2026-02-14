import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://lawncare.center'

export const metadata: Metadata = {
  title: 'About Lawn Care Center - Our Mission & Expert Sources',
  description: 'Learn about Lawn Care Center, our content methodology, expert sources, and commitment to providing accurate, actionable lawn care advice.',
  openGraph: {
    title: 'About Lawn Care Center - Our Mission & Expert Sources',
    description: 'Learn about Lawn Care Center, our content methodology, expert sources, and commitment to providing accurate, actionable lawn care advice.',
    url: `${baseUrl}/about`,
    siteName: 'Lawn Care Center',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary',
    title: 'About Us - Lawn Care Center',
    description: 'Learn about Lawn Care Center and our expert lawn care content.',
  },
  alternates: {
    canonical: `${baseUrl}/about`,
  },
}

export default function AboutPage() {
  const organizationSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${baseUrl}/#organization`,
    name: 'Lawn Care Center',
    url: baseUrl,
    logo: {
      '@type': 'ImageObject',
      url: `${baseUrl}/images/logo_accent.png`,
    },
    description: 'Expert lawn care advice for homeowners. Practical, science-backed guides covering seasonal maintenance, fertilization, aeration, weed control, mowing, and watering.',
    foundingDate: '2025',
    sameAs: [
      'https://github.com/JakeTaylorDesign/lawncare-center',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      email: 'contact@lawncare.center',
      contactType: 'customer service',
    },
    knowsAbout: [
      'Lawn Care',
      'Turfgrass Management',
      'Fertilization',
      'Lawn Aeration',
      'Weed Control',
      'Grass Seed',
      'Lawn Mowing',
      'Irrigation',
    ],
  }

  const websiteSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${baseUrl}/#website`,
    url: baseUrl,
    name: 'Lawn Care Center',
    publisher: { '@id': `${baseUrl}/#organization` },
    potentialAction: {
      '@type': 'SearchAction',
      target: `${baseUrl}/search?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
  }

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [organizationSchema, websiteSchema],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="min-h-screen bg-white">
        <div className="max-w-3xl mx-auto px-4 py-12">
          {/* Breadcrumb */}
          <nav className="text-sm text-gray-500 mb-8" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-grass-600">Home</Link>
            <span className="mx-2">/</span>
            <span className="text-grass-700">About</span>
          </nav>

          <h1 className="text-3xl md:text-4xl font-bold text-grass-900 mb-6">
            About Lawn Care Center
          </h1>

          <div className="prose prose-lg max-w-none prose-headings:text-grass-900">
            <p className="text-xl text-gray-600 mb-8">
              Lawn Care Center provides practical, science-backed lawn care guides for homeowners.
              Our goal is to help you maintain a healthy, beautiful lawn with clear instructions
              you can follow regardless of your experience level.
            </p>

            <h2>Our Mission</h2>
            <p>
              We believe every homeowner deserves access to expert-quality lawn care advice without
              the jargon or upselling. Our articles focus on actionable steps backed by research
              from university extension programs and turfgrass science.
            </p>

            <h2>Content Methodology</h2>
            <p>
              Every article on Lawn Care Center follows a rigorous process to ensure accuracy
              and usefulness:
            </p>
            <ol>
              <li>
                <strong>Research:</strong> Topics are selected based on real search demand and
                seasonal relevance using Google Trends data.
              </li>
              <li>
                <strong>Expert Sources:</strong> Content is informed by university extension
                programs (Penn State, University of Maryland, Michigan State, University of Georgia),
                USDA guidelines, and published turfgrass research.
              </li>
              <li>
                <strong>Video Verification:</strong> We embed relevant tutorials from trusted
                YouTube creators to provide visual demonstrations and additional expert perspectives.
              </li>
              <li>
                <strong>Quality Assurance:</strong> Each article undergoes multi-dimensional
                evaluation for factual accuracy, actionability, SEO optimization, and proper
                source citation.
              </li>
              <li>
                <strong>Regular Updates:</strong> Articles are monitored for freshness and updated
                when new research or best practices emerge.
              </li>
            </ol>

            <h2>What We Cover</h2>
            <ul>
              <li><strong>Seasonal Care:</strong> Spring prep, summer maintenance, fall renovation, winter protection</li>
              <li><strong>Fertilization:</strong> Timing, types, organic vs synthetic, application techniques</li>
              <li><strong>Aeration & Dethatching:</strong> When, how, and equipment selection</li>
              <li><strong>Weed Control:</strong> Pre-emergent timing, selective herbicides, organic alternatives</li>
              <li><strong>Mowing:</strong> Height settings, frequency, striping, equipment maintenance</li>
              <li><strong>Watering:</strong> Schedules, deep watering, drought management, irrigation systems</li>
              <li><strong>Grass Types:</strong> Cool-season vs warm-season, shade tolerance, climate zones</li>
              <li><strong>Problem Solving:</strong> Brown patches, bare spots, pests, diseases, compaction</li>
              <li><strong>Equipment:</strong> Robot mowers, string trimmers, spreaders, aerators</li>
            </ul>

            <h2>AI-Assisted Content</h2>
            <p>
              Lawn Care Center uses AI technology to assist in content creation. Our articles are
              generated with the help of large language models and then verified against expert
              sources. This approach allows us to produce comprehensive guides at scale while
              maintaining accuracy through our citation and quality assurance process.
            </p>
            <p>
              All factual claims in our articles are supported by citations from university
              extension programs, government agricultural agencies, or established industry
              sources. We are transparent about our methodology because we believe readers
              deserve to know how content is produced.
            </p>

            <h2>Affiliate Disclosure</h2>
            <p>
              Some articles contain affiliate links to products on Amazon. If you purchase through
              these links, we may earn a small commission at no extra cost to you. This helps
              support the site and allows us to continue providing free lawn care advice.
              Product recommendations are based on relevance and quality, not commission rates.
              See our full <Link href="/affiliate-disclosure" className="text-grass-600 hover:text-grass-800">affiliate disclosure</Link> for details.
            </p>

            <h2>Contact Us</h2>
            <p>
              Have a question, suggestion, or correction? We welcome feedback.
            </p>
            <ul>
              <li><strong>Email:</strong> <a href="mailto:contact@lawncare.center" className="text-grass-600 hover:text-grass-800">contact@lawncare.center</a></li>
              <li><strong>Website:</strong> <a href="https://lawncare.center" className="text-grass-600 hover:text-grass-800">lawncare.center</a></li>
            </ul>

            <h2>Our Sources</h2>
            <p>We regularly cite and reference the following institutions:</p>
            <ul>
              <li>Penn State Extension - Turfgrass Science Program</li>
              <li>University of Maryland Extension - Lawn Care</li>
              <li>Michigan State University Extension - Turfgrass Management</li>
              <li>University of Georgia Extension - Lawn and Garden</li>
              <li>USDA Natural Resources Conservation Service</li>
              <li>Scotts Miracle-Gro Research</li>
              <li>National Turfgrass Evaluation Program (NTEP)</li>
            </ul>
          </div>

          {/* Footer nav */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <Link href="/articles" className="text-grass-600 hover:text-grass-800 font-medium">
              Browse All Articles
            </Link>
          </div>
        </div>
      </div>
    </>
  )
}
