import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://thegreenleaf.com'

export const metadata: Metadata = {
  title: 'About The Strain Report - Our Mission & Expert Sources',
  description: 'Learn about The Strain Report, our content methodology, expert sources, and commitment to providing accurate, balanced cannabis education.',
  openGraph: {
    title: 'About The Strain Report - Our Mission & Expert Sources',
    description: 'Learn about The Strain Report, our content methodology, expert sources, and commitment to providing accurate, balanced cannabis education.',
    url: `${baseUrl}/about`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary',
    title: 'About Us - The Strain Report',
    description: 'Learn about The Strain Report and our expert cannabis education content.',
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
    name: 'The Strain Report',
    url: baseUrl,
    logo: {
      '@type': 'ImageObject',
      url: `${baseUrl}/images/logo_accent.png`,
    },
    description: 'Cannabis education, strain guides, growing tips, and wellness content. Accurate, balanced information for responsible cannabis consumers and cultivators.',
    foundingDate: '2025',
    contactPoint: {
      '@type': 'ContactPoint',
      email: 'contact@thegreenleaf.com',
      contactType: 'customer service',
    },
    knowsAbout: [
      'Cannabis Cultivation',
      'Cannabis Strains',
      'CBD and Wellness',
      'Cannabis Edibles',
      'Growing Equipment',
      'Cannabis Science',
      'Cannabis Law',
      'Terpene Profiles',
    ],
  }

  const websiteSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${baseUrl}/#website`,
    url: baseUrl,
    name: 'The Strain Report',
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
            <Link href="/" className="hover:text-leaf-600">Home</Link>
            <span className="mx-2">/</span>
            <span className="text-leaf-700">About</span>
          </nav>

          <h1 className="text-3xl md:text-4xl font-bold text-leaf-900 mb-6">
            About The Strain Report
          </h1>

          <div className="prose prose-lg max-w-none prose-headings:text-leaf-900">
            <p className="text-xl text-gray-600 mb-8">
              The Strain Report provides accurate, balanced cannabis education for consumers and cultivators.
              Our goal is to help you make informed decisions with clear, research-backed guides
              regardless of your experience level.
            </p>

            <h2>Our Mission</h2>
            <p>
              We believe everyone deserves access to accurate cannabis information without
              hype or misinformation. Our articles focus on science-backed education covering
              strains, cultivation, consumption methods, health and wellness, and legal developments.
            </p>

            <h2>Content Methodology</h2>
            <p>
              Every article on The Strain Report follows a rigorous process to ensure accuracy
              and usefulness:
            </p>
            <ol>
              <li>
                <strong>Research:</strong> Topics are selected based on real search demand and
                seasonal relevance using Google Trends data.
              </li>
              <li>
                <strong>Expert Sources:</strong> Content is informed by peer-reviewed research
                from the Journal of Cannabis Research, Project CBD, NORML, and established
                industry publications.
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
                when new research, regulations, or best practices emerge.
              </li>
            </ol>

            <h2>What We Cover</h2>
            <ul>
              <li><strong>Strains & Genetics:</strong> Indica, sativa, hybrid profiles, terpene guides, and strain reviews</li>
              <li><strong>Growing & Cultivation:</strong> Indoor, outdoor, hydroponics, soil, lighting, and nutrient schedules</li>
              <li><strong>Consumption Methods:</strong> Smoking, edibles, tinctures, vaping, topicals, and concentrates</li>
              <li><strong>Health & Wellness:</strong> CBD benefits, medical cannabis, pain relief, anxiety, and sleep</li>
              <li><strong>Legal & Industry:</strong> State-by-state laws, legalization news, regulations, and licensing</li>
              <li><strong>Culture & Lifestyle:</strong> History, recipes, events, travel guides, and accessories</li>
            </ul>

            <h2>AI-Assisted Content</h2>
            <p>
              The Strain Report uses AI technology to assist in content creation. Our articles are
              generated with the help of large language models and then verified against expert
              sources. This approach allows us to produce comprehensive guides at scale while
              maintaining accuracy through our citation and quality assurance process.
            </p>
            <p>
              All factual claims in our articles are supported by citations from peer-reviewed
              research, government agencies, or established industry sources. We are transparent
              about our methodology because we believe readers deserve to know how content is produced.
            </p>

            <h2>Legal Disclaimer</h2>
            <p>
              Cannabis laws vary by state and jurisdiction. Content on The Strain Report is for
              educational purposes only and should not be considered legal or medical advice.
              Always check your local laws before purchasing, possessing, or cultivating cannabis.
              See our full <Link href="/disclaimer" className="text-leaf-600 hover:text-leaf-800">legal disclaimer</Link> for details.
            </p>

            <h2>Affiliate Disclosure</h2>
            <p>
              Some articles contain affiliate links to products on Amazon. If you purchase through
              these links, we may earn a small commission at no extra cost to you. This helps
              support the site and allows us to continue providing free cannabis education.
              Product recommendations are based on relevance and quality, not commission rates.
              See our full <Link href="/affiliate-disclosure" className="text-leaf-600 hover:text-leaf-800">affiliate disclosure</Link> for details.
            </p>

            <h2>Contact Us</h2>
            <p>
              Have a question, suggestion, or correction? We welcome feedback.
            </p>
            <ul>
              <li><strong>Email:</strong> <a href="mailto:contact@thegreenleaf.com" className="text-leaf-600 hover:text-leaf-800">contact@thegreenleaf.com</a></li>
              <li><strong>Website:</strong> <a href="https://thegreenleaf.com" className="text-leaf-600 hover:text-leaf-800">thegreenleaf.com</a></li>
            </ul>

            <h2>Our Sources</h2>
            <p>We regularly cite and reference the following sources:</p>
            <ul>
              <li>Leafly - Comprehensive strain database and cannabis guides</li>
              <li>NORML - Cannabis law and policy research</li>
              <li>Project CBD - CBD and medical cannabis research</li>
              <li>Cannabis Business Times - Industry cultivation best practices</li>
              <li>Journal of Cannabis Research - Peer-reviewed cannabis science</li>
              <li>Americans for Safe Access - Medical cannabis patient resources</li>
              <li>Marijuana Policy Project - Cannabis policy analysis</li>
            </ul>
          </div>

          {/* Footer nav */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <Link href="/articles" className="text-leaf-600 hover:text-leaf-800 font-medium">
              Browse All Articles
            </Link>
          </div>
        </div>
      </div>
    </>
  )
}
