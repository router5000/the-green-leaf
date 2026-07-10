import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Affiliate Disclosure - Our Product Partnerships | The Strain Report',
  description: 'Affiliate disclosure and transparency information for The Strain Report. Learn about our affiliate partnerships and how we earn commissions.',
  openGraph: {
    title: 'Affiliate Disclosure - Our Product Partnerships | The Strain Report',
    description: 'Affiliate disclosure and transparency information. Learn about our affiliate partnerships.',
    url: `${baseUrl}/affiliate-disclosure`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-default.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Strain Report - Affiliate Disclosure',
    }],
  },
  twitter: {
    card: 'summary',
    title: 'Affiliate Disclosure - Our Product Partnerships | The Strain Report',
    description: 'Affiliate disclosure and transparency information for The Strain Report.',
  },
  alternates: {
    canonical: `${baseUrl}/affiliate-disclosure`,
  },
}

export default function AffiliateDisclosurePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-leaf-900 mb-8">Affiliate Disclosure</h1>

      <div className="prose prose-lg max-w-none">
        <p className="text-gray-600 mb-6">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Transparency Commitment</h2>
          <p className="text-gray-700 leading-relaxed">
            At The Strain Report, we believe in full transparency with our readers. This page explains our affiliate relationships and how we may earn commissions from product recommendations on our website.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">What Are Affiliate Links?</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            Affiliate links are special tracking links that allow us to earn a commission when you purchase products through our recommendations. When you click an affiliate link and make a purchase, the retailer pays us a small percentage of the sale at no additional cost to you.
          </p>
          <p className="text-gray-700 leading-relaxed">
            These commissions help support our website, allowing us to continue creating free, high-quality cannabis content for our readers.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Affiliate Programs We Participate In</h2>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Amazon Associates</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            The Strain Report is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com.
          </p>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Other Affiliate Partnerships</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            We may also participate in affiliate programs with:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Home Depot</li>
            <li>Lowe's</li>
            <li>Cannabis equipment manufacturers</li>
            <li>Garden supply retailers</li>
            <li>Other relevant cannabis and gardening companies</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Our Recommendation Policy</h2>

          <div className="bg-leaf-50 border-l-4 border-leaf-500 p-6 mb-6">
            <h3 className="text-lg font-semibold text-leaf-900 mb-3">Our Promise to You</h3>
            <p className="text-gray-700 leading-relaxed mb-2">
              We only recommend products and services that we genuinely believe will provide value to our readers. Our editorial content is never influenced by affiliate relationships.
            </p>
          </div>

          <p className="text-gray-700 leading-relaxed mb-4">
            <strong>How We Choose Products:</strong>
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>We research products thoroughly before recommending them</li>
            <li>We prioritize quality, effectiveness, and value</li>
            <li>We consider user reviews and expert opinions</li>
            <li>We test products when possible</li>
            <li>We disclose both pros and cons honestly</li>
          </ul>

          <p className="text-gray-700 leading-relaxed">
            <strong>Important:</strong> Whether we earn a commission or not does not affect the price you pay. Affiliate links do not increase the cost of products for you.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">How to Identify Affiliate Links</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            We make it easy to identify when you're clicking an affiliate link:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Product recommendation boxes clearly indicate affiliate partnerships</li>
            <li>Articles containing affiliate links include a disclosure notice</li>
            <li>Links to external retailers are typically affiliate links</li>
            <li>We may use phrases like "as an Amazon Associate, we earn from qualifying purchases"</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Your Support Helps Us</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            When you purchase products through our affiliate links, you're supporting The Strain Report at no extra cost to you. This support enables us to:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Create comprehensive, research-based cannabis guides</li>
            <li>Maintain and improve our website</li>
            <li>Test and review cannabis products</li>
            <li>Provide free, ad-supported content to all readers</li>
            <li>Continue expanding our library of helpful resources</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Non-Affiliated Recommendations</h2>
          <p className="text-gray-700 leading-relaxed">
            Not all products or services mentioned on our website are affiliated. We may recommend products simply because we believe they're valuable to our readers, regardless of whether we have an affiliate relationship. When in doubt, assume that links to external retailers are affiliate links.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Questions About Our Affiliates</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            If you have questions about our affiliate relationships or would like to know whether a specific link is an affiliate link, please contact us:
          </p>
          <ul className="list-none text-gray-700">
            <li>Email: affiliates@strainreport.com</li>
            <li>Website: <Link href="/" className="text-leaf-600 hover:text-leaf-800 underline">strainreport.com</Link></li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">FTC Compliance</h2>
          <p className="text-gray-700 leading-relaxed">
            This disclosure is in accordance with the Federal Trade Commission's 16 CFR, Part 255: "Guides Concerning the Use of Endorsements and Testimonials in Advertising." We comply with all FTC guidelines regarding affiliate relationships and product endorsements.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Updates to This Disclosure</h2>
          <p className="text-gray-700 leading-relaxed">
            We may update this affiliate disclosure from time to time to reflect new partnerships or changes in our affiliate relationships. The "Last Updated" date at the top of this page indicates when this disclosure was last revised.
          </p>
        </section>

        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            <Link href="/privacy-policy" className="text-leaf-600 hover:text-leaf-800 mr-4">Privacy Policy</Link>
            <Link href="/terms-of-service" className="text-leaf-600 hover:text-leaf-800 mr-4">Terms of Service</Link>
            <Link href="/" className="text-leaf-600 hover:text-leaf-800">← Back to Home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
