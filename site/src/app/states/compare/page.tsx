import type { Metadata } from 'next'
import Link from 'next/link'
import CompareTable from './CompareTable'
import { getCompareRows, TIER_BADGE, TIER_LABEL, type StatusTier } from '@/data/statesCompare'
import { STATES_LAST_REVIEWED } from '@/data/statesContent'

const baseUrl = 'https://strainreport.com'
const pageUrl = `${baseUrl}/states/compare`
const csvUrl = `${baseUrl}/states/cannabis-laws.csv`

export const metadata: Metadata = {
  title: 'Cannabis Laws by State: Comparison Table | The Strain Report',
  description: 'Compare cannabis laws in all 50 US states side by side: legal status, possession limits, home grow, minimum age, dispensary sales, and public use. Free CSV download.',
  alternates: { canonical: pageUrl },
  openGraph: {
    title: 'Cannabis Laws by State: Comparison Table',
    description: 'All 50 states side by side: status, possession limits, home grow, age, sales, and public use.',
    url: pageUrl,
    siteName: 'The Strain Report',
    type: 'website',
  },
}

const embedSnippet = `<p>Source: <a href="${pageUrl}">Cannabis Laws by State</a> — The Strain Report (strainreport.com)</p>`

export default function StatesComparePage() {
  const rows = getCompareRows()
  const datasetSchema = {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: 'Cannabis laws by US state',
    description: 'Legal status, possession limits, home-grow rules, minimum age, dispensary sales status, and public-use rules for cannabis in all 50 US states. General information, not legal advice.',
    url: pageUrl,
    keywords: ['cannabis laws', 'marijuana laws by state', 'possession limits', 'home grow', 'medical marijuana'],
    isAccessibleForFree: true,
    license: 'https://creativecommons.org/licenses/by/4.0/',
    creator: { '@type': 'Organization', '@id': `${baseUrl}/#organization`, name: 'The Strain Report', url: baseUrl },
    spatialCoverage: { '@type': 'Place', name: 'United States' },
    temporalCoverage: '2026-10',
    dateModified: '2026-10-19',
    variableMeasured: ['legal status', 'possession limit', 'home grow', 'minimum age', 'dispensary sales open', 'public use'],
    distribution: [{ '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: csvUrl }],
  }
  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: baseUrl },
      { '@type': 'ListItem', position: 2, name: 'States', item: `${baseUrl}/states` },
      { '@type': 'ListItem', position: 3, name: 'Compare', item: pageUrl },
    ],
  }

  return (
    <div className="bg-[#f0f0f0]">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>
      <div className="max-w-7xl mx-auto px-4 py-3">
        <nav className="flex items-center gap-1.5 text-sm text-neutral-400" aria-label="Breadcrumb">
          <Link href="/" className="hover:text-leaf-700 transition-colors">Home</Link>
          <span>/</span>
          <Link href="/states" className="hover:text-leaf-700 transition-colors">States</Link>
          <span>/</span>
          <span className="text-neutral-700 font-medium">Compare</span>
        </nav>
      </div>

      <section className="max-w-7xl mx-auto px-4 pb-16">
        <header className="py-6">
          <h1 className="text-3xl md:text-5xl font-bold mb-3" style={{ color: '#1a3a0a' }}>Cannabis Laws by State: Comparison Table</h1>
          <p className="text-lg max-w-3xl" style={{ color: '#2d4a1e' }}>
            All 50 states side by side: legal status, possession limits, home grow, minimum age, whether dispensary sales are open, and public-use rules. Last reviewed {STATES_LAST_REVIEWED}.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <a href="/states/cannabis-laws.csv" download className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium bg-[#1a3a0a] text-white hover:bg-[#2d5016] transition-colors no-underline">
              Download CSV
            </a>
            <Link href="/states" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium bg-white text-neutral-800 shadow-sm hover:bg-neutral-50 no-underline">
              Browse state guides
            </Link>
          </div>
        </header>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mb-5 text-xs text-neutral-600" aria-label="Status legend">
          <span className="font-semibold text-neutral-700">Legend:</span>
          {(['recreational', 'medical', 'cbd-only', 'illegal'] as StatusTier[]).map(t => (
            <span key={t} className="inline-flex items-center gap-1.5">
              <span className={`px-2 py-0.5 rounded-full font-medium ${TIER_BADGE[t]}`}>{TIER_LABEL[t]}</span>
              <span>
                {t === 'recreational' && 'adults 21+ may possess cannabis'}
                {t === 'medical' && 'registered patients only'}
                {t === 'cbd-only' && 'restricted low-THC program'}
                {t === 'illegal' && 'no legal program'}
              </span>
            </span>
          ))}
        </div>

        <CompareTable rows={rows} />

        <div className="grid md:grid-cols-2 gap-4 mt-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border-l-4 border-amber-400">
            <h2 className="text-lg font-bold text-neutral-900 mb-2">Laws change. This is not legal advice.</h2>
            <p className="text-sm text-neutral-600 leading-relaxed">
              This table summarizes state rules as of our last review and simplifies details such as concentrate limits, local ordinances, and medical-program specifics. Federal law still prohibits marijuana, including carrying it across state lines. Always confirm with each state&apos;s official source (linked on every state page) or a licensed attorney before relying on any detail.
            </p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-neutral-900 mb-2">Cite or embed this table</h2>
            <p className="text-sm text-neutral-600 mb-3">
              Free to reuse under CC BY 4.0 with attribution. Copy this link snippet, or download the <a href="/states/cannabis-laws.csv" className="text-leaf-700 underline">CSV</a>.
            </p>
            <pre className="text-xs bg-neutral-50 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap break-all"><code>{embedSnippet}</code></pre>
          </div>
        </div>
      </section>
    </div>
  )
}
