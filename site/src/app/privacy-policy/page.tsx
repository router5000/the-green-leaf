import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://thegreenleaf.com'

export const metadata: Metadata = {
  title: 'Privacy Policy - How We Protect Your Data | The Green Leaf',
  description: 'Privacy policy for The Green Leaf website. Learn how we collect, use, and protect your personal information.',
  openGraph: {
    title: 'Privacy Policy - How We Protect Your Data | The Green Leaf',
    description: 'Privacy policy for The Green Leaf website. Learn how we collect, use, and protect your personal information.',
    url: `${baseUrl}/privacy-policy`,
    siteName: 'The Green Leaf',
    type: 'website',
    locale: 'en_US',
    images: [{
      url: `${baseUrl}/images/og-default.jpg`,
      width: 1200,
      height: 630,
      alt: 'The Green Leaf - Privacy Policy',
    }],
  },
  twitter: {
    card: 'summary',
    title: 'Privacy Policy - How We Protect Your Data | The Green Leaf',
    description: 'Privacy policy for The Green Leaf website.',
  },
  alternates: {
    canonical: `${baseUrl}/privacy-policy`,
  },
}

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-leaf-900 mb-8">Privacy Policy</h1>

      <div className="prose prose-lg max-w-none">
        <p className="text-gray-600 mb-6">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Introduction</h2>
          <p className="text-gray-700 leading-relaxed">
            The Green Leaf ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website thegreenleaf.com.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Information We Collect</h2>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Automatically Collected Information</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            When you visit our website, we automatically collect certain information about your device, including:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Browser type and version</li>
            <li>Operating system</li>
            <li>IP address</li>
            <li>Pages visited and time spent on pages</li>
            <li>Referring website addresses</li>
            <li>Device identifiers</li>
          </ul>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Information You Provide</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            We may collect information you voluntarily provide when you:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Subscribe to our newsletter</li>
            <li>Contact us via email</li>
            <li>Leave comments on articles (if enabled)</li>
            <li>Fill out forms on our website</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">How We Use Your Information</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            We use the information we collect to:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>Provide, operate, and maintain our website</li>
            <li>Improve, personalize, and expand our website</li>
            <li>Understand and analyze how you use our website</li>
            <li>Develop new features, products, and services</li>
            <li>Communicate with you, including for customer service and updates</li>
            <li>Send you marketing and promotional communications (with your consent)</li>
            <li>Monitor and analyze usage and trends</li>
            <li>Detect, prevent, and address technical issues and fraud</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Cookies and Tracking Technologies</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            We use cookies and similar tracking technologies to track activity on our website and store certain information. Cookies are files with a small amount of data that may include an anonymous unique identifier.
          </p>
          <p className="text-gray-700 leading-relaxed mb-4">
            You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, if you do not accept cookies, you may not be able to use some portions of our website.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Third-Party Services</h2>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Google Analytics</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            We use Google Analytics to monitor and analyze website traffic. Google Analytics is a web analytics service that tracks and reports website traffic. Google uses the data collected to track and monitor the use of our website. For more information on Google's privacy practices, visit{' '}
            <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-leaf-600 hover:text-leaf-800 underline">
              Google Privacy & Terms
            </a>.
          </p>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Google AdSense</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            We use Google AdSense to display advertisements on our website. Google AdSense uses cookies to serve ads based on your prior visits to our website or other websites. You may opt out of personalized advertising by visiting{' '}
            <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer" className="text-leaf-600 hover:text-leaf-800 underline">
              Google Ads Settings
            </a>.
          </p>

          <h3 className="text-xl font-semibold text-leaf-700 mb-3">Affiliate Programs</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            We participate in affiliate marketing programs, which means we may earn commissions on purchases made through our affiliate links. These programs may use cookies to track sales. For more information, please see our{' '}
            <Link href="/affiliate-disclosure" className="text-leaf-600 hover:text-leaf-800 underline">
              Affiliate Disclosure
            </Link>.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Data Security</h2>
          <p className="text-gray-700 leading-relaxed">
            We implement appropriate technical and organizational security measures to protect your personal information. However, no method of transmission over the Internet or electronic storage is 100% secure, and we cannot guarantee absolute security.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Your Data Rights</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            Depending on your location, you may have certain rights regarding your personal information, including:
          </p>
          <ul className="list-disc pl-6 mb-4 text-gray-700">
            <li>The right to access your personal information</li>
            <li>The right to request correction of inaccurate data</li>
            <li>The right to request deletion of your data</li>
            <li>The right to object to or restrict processing</li>
            <li>The right to data portability</li>
            <li>The right to withdraw consent</li>
          </ul>
          <p className="text-gray-700 leading-relaxed">
            To exercise these rights, please contact us using the information provided below.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Children's Privacy</h2>
          <p className="text-gray-700 leading-relaxed">
            Our website is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13. If you become aware that a child has provided us with personal information, please contact us.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Changes to This Privacy Policy</h2>
          <p className="text-gray-700 leading-relaxed">
            We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date. You are advised to review this Privacy Policy periodically for any changes.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-leaf-800 mb-4">Contact Us</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            If you have any questions about this Privacy Policy, please contact us:
          </p>
          <ul className="list-none text-gray-700">
            <li>Email: privacy@thegreenleaf.com</li>
            <li>Website: <Link href="/" className="text-leaf-600 hover:text-leaf-800 underline">thegreenleaf.com</Link></li>
          </ul>
        </section>

        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            <Link href="/" className="text-leaf-600 hover:text-leaf-800">← Back to Home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
