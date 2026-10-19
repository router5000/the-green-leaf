import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Contact The Strain Report',
  description: 'How to contact The Strain Report about corrections, editorial questions, partnerships, and privacy requests.',
  alternates: { canonical: `${baseUrl}/contact` },
  openGraph: { title: 'Contact The Strain Report', url: `${baseUrl}/contact`, siteName: 'The Strain Report', type: 'website' },
}

export default function ContactPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-leaf-900 mb-8">Contact Us</h1>
      <div className="prose prose-lg max-w-none">
        <p>
          The Strain Report is an independent cannabis education site publishing strain profiles, growing and
          consumption guides, terpene explainers, and state-by-state summaries of cannabis laws. We read every
          message and aim to reply within a few business days.
        </p>
        <h2>Email</h2>
        <p>
          The best way to reach us is by email at{' '}
          <a href="mailto:info@strainreport.com">info@strainreport.com</a>.
        </p>
        <h2>Corrections and fact-checks</h2>
        <p>
          Accuracy matters to us, especially on legal and health topics. If you spot an outdated law, a wrong
          figure, or a broken source link, email us with the page URL and, if possible, a link to an official or
          primary source. We review correction requests and update pages when the evidence supports a change.
        </p>
        <h2>Editorial, partnerships, and press</h2>
        <p>
          For editorial questions, content partnerships, or media inquiries, use the same address and include a
          short description of your request. We do not accept payment to change editorial conclusions; see our{' '}
          <Link href="/affiliate-disclosure">affiliate disclosure</Link> for how we handle affiliate links.
        </p>
        <h2>Privacy requests</h2>
        <p>
          To ask about personal data or unsubscribe from the newsletter, email us or see the{' '}
          <Link href="/privacy-policy">privacy policy</Link>.
        </p>
        <p className="text-sm text-gray-500">
          The Strain Report provides general information only. We cannot give medical or legal advice; please
          consult a qualified professional or your state&apos;s official resources.
        </p>
      </div>
    </div>
  )
}
