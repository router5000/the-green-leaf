import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Terms of Service - Usage Guidelines | The Strain Report',
  description: 'Terms of service for using The Strain Report website. Please read these terms carefully before using our site.',
  openGraph: {
    title: 'Terms of Service - Usage Guidelines | The Strain Report',
    description: 'Terms of service for using The Strain Report website. Please read these terms carefully.',
    url: `${baseUrl}/terms-of-service`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-default.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Strain Report - Terms of Service',
    }],
  },
  twitter: {
    card: 'summary',
    title: 'Terms of Service - Usage Guidelines | The Strain Report',
    description: 'Terms of service for using The Strain Report website.',
  },
  alternates: {
    canonical: `${baseUrl}/terms-of-service`,
  },
}

export default function TermsOfServicePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-leaf-900 mb-8">Terms of Service</h1>

      <div className="prose prose-lg max-w-none">
        <p className="text-gray-600 mb-6">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Agreement to Terms</h2>
          <p className="text-gray-700 leading-relaxed">
            By accessing or using The Strain Report ("the Website"), you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of these Terms, you may not access the Website.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Use of Website</h2>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Permitted Use</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            You may use our Website for lawful purposes only. You agree to use the Website in accordance with all applicable laws and regulations.
          </p>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Prohibited Activities</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            You may not:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Use the Website in any way that violates any applicable federal, state, local, or international law</li>
            <li>Attempt to gain unauthorized access to any portion of the Website</li>
            <li>Interfere with or disrupt the Website or servers or networks connected to the Website</li>
            <li>Use any automated system to access the Website for any purpose without our express written permission</li>
            <li>Transmit any viruses, worms, defects, Trojan horses, or other malicious code</li>
            <li>Attempt to impersonate another user or person</li>
            <li>Use the Website to transmit spam or unsolicited messages</li>
            <li>Scrape or harvest content from the Website without permission</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Intellectual Property Rights</h2>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Our Content</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            Unless otherwise indicated, the Website and all content, including but not limited to text, graphics, logos, images, articles, and software, are the property of The Strain Report and are protected by copyright, trademark, and other intellectual property laws.
          </p>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Limited License</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            We grant you a limited, non-exclusive, non-transferable license to access and use the Website for personal, non-commercial purposes. This license does not include:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Resale or commercial use of the Website or its contents</li>
            <li>Collection and use of product listings, descriptions, or prices</li>
            <li>Derivative use of the Website or its contents</li>
            <li>Downloading or copying account information for the benefit of another merchant</li>
            <li>Use of data mining, robots, or similar data gathering and extraction tools</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">User-Generated Content</h2>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Comments and Submissions</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            If you submit comments, feedback, or other content to the Website ("User Content"), you grant us a non-exclusive, worldwide, royalty-free, perpetual, irrevocable license to use, reproduce, modify, publish, and distribute such User Content.
          </p>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Responsibility for User Content</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            You are solely responsible for your User Content. You represent and warrant that:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>You own or have the necessary rights to submit the User Content</li>
            <li>Your User Content does not violate any third-party rights</li>
            <li>Your User Content does not contain unlawful, harmful, or offensive material</li>
            <li>Your User Content does not violate any applicable laws or regulations</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Disclaimers and Limitations</h2>

          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 mb-6">
            <h3 className="text-lg font-semibold text-yellow-900 mb-3">Important Notice</h3>
            <p className="text-gray-700 leading-relaxed">
              The information on this Website is provided for general informational purposes only. We are not professional cannabis specialists, and our content should not be considered professional advice.
            </p>
          </div>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">No Warranties</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            THE WEBSITE IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS. WE MAKE NO WARRANTIES, EXPRESSED OR IMPLIED, REGARDING:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>The accuracy, reliability, or completeness of content on the Website</li>
            <li>The availability or uninterrupted access to the Website</li>
            <li>The results that may be obtained from using the Website</li>
            <li>The correction of errors or defects in the Website</li>
          </ul>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Limitation of Liability</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE GREEN LEAF SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES RESULTING FROM:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Your access to or use of or inability to access or use the Website</li>
            <li>Any conduct or content of any third party on the Website</li>
            <li>Any content obtained from the Website</li>
            <li>Unauthorized access, use, or alteration of your transmissions or content</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Product Recommendations and Affiliate Links</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            The Website may contain affiliate links to third-party products and services. We may earn commissions from purchases made through these links. For more information, please see our{' '}
            <Link href="/affiliate-disclosure" className="text-leaf-600 hover:text-leaf-800 underline">
              Affiliate Disclosure
            </Link>.
          </p>
          <p className="text-gray-700 leading-relaxed">
            We are not responsible for the products or services offered by third parties, and your purchase and use of such products or services is at your own risk.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">External Links</h2>
          <p className="text-gray-700 leading-relaxed">
            The Website may contain links to external websites that are not operated by us. We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party websites. You acknowledge and agree that we shall not be responsible or liable for any damage or loss caused by your use of any third-party websites.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Indemnification</h2>
          <p className="text-gray-700 leading-relaxed">
            You agree to defend, indemnify, and hold harmless The Strain Report and its officers, directors, employees, and agents from and against any claims, liabilities, damages, losses, and expenses, including reasonable attorneys' fees, arising out of or in any way connected with your access to or use of the Website or your violation of these Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Changes to Terms</h2>
          <p className="text-gray-700 leading-relaxed">
            We reserve the right to modify or replace these Terms at any time at our sole discretion. If we make material changes to these Terms, we will provide notice by updating the "Last Updated" date. Your continued use of the Website after any such changes constitutes your acceptance of the new Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Termination</h2>
          <p className="text-gray-700 leading-relaxed">
            We may terminate or suspend your access to the Website immediately, without prior notice or liability, for any reason, including if you breach these Terms. Upon termination, your right to use the Website will immediately cease.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Governing Law</h2>
          <p className="text-gray-700 leading-relaxed">
            These Terms shall be governed by and construed in accordance with the laws of the United States, without regard to its conflict of law provisions. Any legal action or proceeding arising under these Terms will be brought exclusively in the courts located in the United States.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Contact Information</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            If you have any questions about these Terms, please contact us:
          </p>
          <ul className="list-none text-gray-700">
            <li>Email: legal@strainreport.com</li>
            <li>Website: <Link href="/" className="text-leaf-600 hover:text-leaf-800 underline">strainreport.com</Link></li>
          </ul>
        </section>

        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            <Link href="/privacy-policy" className="text-leaf-600 hover:text-leaf-800 mr-4">Privacy Policy</Link>
            <Link href="/affiliate-disclosure" className="text-leaf-600 hover:text-leaf-800 mr-4">Affiliate Disclosure</Link>
            <Link href="/" className="text-leaf-600 hover:text-leaf-800">← Back to Home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
