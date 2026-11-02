const { execSync } = require('child_process')

// Build-time "template last changed" dates for sitemap lastmod (see
// src/lib/contentDates.ts). Each group is the newest git commit date that
// touched any of its paths; falls back to the build date when git history is
// unavailable (e.g. no .git or the paths predate a shallow clone).
const BUILD_DATE = new Date().toISOString()
function gitDate(paths) {
  try {
    const out = execSync(`git log -1 --format=%cI -- ${paths.map((p) => `"${p}"`).join(' ')}`, {
      cwd: __dirname,
      stdio: ['ignore', 'pipe', 'ignore'],
    }).toString().trim()
    return out ? new Date(out).toISOString() : BUILD_DATE
  } catch {
    return BUILD_DATE
  }
}
const CONTENT_DATE_GROUPS = {
  strain: ['src/app/strains/[slug]', 'src/lib/strainCatalog.ts', 'src/lib/strainMetaDescription.ts', 'src/lib/formatRange.ts', 'src/lib/strainArticleLinks.ts', 'src/components/RelatedArticlesForStrain.tsx'],
  strainHub: ['src/app/strains/page.tsx', 'src/app/strains/indica', 'src/app/strains/sativa', 'src/app/strains/hybrid', 'src/app/strains/a-z', 'src/components/StrainsListing.tsx', 'src/components/StrainCard.tsx'],
  compare: ['src/app/strains/compare', 'src/data/strainComparisonPairs.ts', 'src/lib/strainComparisons.ts', 'src/lib/formatRange.ts'],
  states: ['src/app/states', 'src/data/statesData.ts', 'src/data/statesContent.ts', 'src/data/statesCompare.ts'],
  terpenes: ['src/app/terpenes', 'src/lib/terpenes.ts'],
  home: ['src/app/page.tsx', 'src/components/ui/Showcase2.tsx', 'src/components/GlobeSection.tsx'],
  about: ['src/app/about'],
  contact: ['src/app/contact'],
  privacy: ['src/app/privacy-policy'],
  terms: ['src/app/terms-of-service'],
  affiliate: ['src/app/affiliate-disclosure'],
  videos: ['src/app/videos'],
  topics: ['src/app/topics'],
  articles: ['src/app/articles'],
}
const CONTENT_DATES = JSON.stringify({
  build: BUILD_DATE,
  ...Object.fromEntries(Object.entries(CONTENT_DATE_GROUPS).map(([k, paths]) => [k, gitDate(paths)])),
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: { CONTENT_DATES },
  output: 'standalone',
  trailingSlash: false,
  async headers() {
    const link = [
      '</llms.txt>; rel="describedby"; type="text/markdown"',
      '</.well-known/api-catalog>; rel="api-catalog"',
      '</openapi.json>; rel="service-desc"; type="application/openapi+json"',
      '</sitemap.xml>; rel="sitemap"; type="application/xml"',
    ].join(', ')
    return [
      { source: '/', headers: [{ key: 'Link', value: link }] },
      { source: '/((?!api/|_next/).*)', headers: [{ key: 'Vary', value: 'Accept' }] },
    ]
  },
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'img.youtube.com',
        pathname: '/vi/**',
      },
      {
        protocol: 'https',
        hostname: 'i.ytimg.com',
        pathname: '/**',
      },
    ],
  },
}

module.exports = nextConfig
