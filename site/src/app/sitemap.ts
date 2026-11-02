import { MetadataRoute } from 'next'
import { getSortedPostsData } from '@/lib/posts'
import { getStrainCatalogSafe, isThinStrain } from '@/lib/strainCatalog'
import { topicClusters, matchesCluster } from '@/app/topics/topicClusters'
import { getAllComparisonPairs } from '@/lib/strainComparisons'
import { templateDate, latestDate } from '@/lib/contentDates'
import { TERPENE_SLUGS } from '@/lib/terpenes'
import { statesData } from '@/data/statesData'

export const revalidate = 86400

const baseUrl = 'https://strainreport.com'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = getSortedPostsData()
  const catalog = await getStrainCatalogSafe()

  // Real lastmod sources instead of new Date() (which told Google every page
  // changed on every crawl).
  const postDate = (p: (typeof posts)[number]) => {
    const gen = new Date(p.generated_at)
    const last = p.last_updated ? new Date(p.last_updated) : null
    return last && last > gen ? last : gen
  }
  // A page changes when its data changes OR its template changes (git date
  // of the template files, computed at build — see src/lib/contentDates.ts).
  const strainTpl = templateDate('strain')
  const hubTpl = templateDate('strainHub')
  const compareTpl = templateDate('compare')
  const statesTpl = templateDate('states')
  const maxDate = (dates: Date[], fallback: Date) => {
    const valid = dates.filter((d) => !isNaN(d.getTime()))
    return valid.length ? new Date(Math.max(...valid.map((d) => d.getTime()))) : fallback
  }
  const latestPost = maxDate(posts.map(postDate), templateDate('articles'))
  const latestStrain = maxDate([hubTpl, ...catalog.map((s) => new Date(s.updated_at ?? ''))], hubTpl)
  const latestStrainOfType = (t: string) =>
    maxDate([hubTpl, ...catalog.filter((s) => s.strain_type === t).map((s) => new Date(s.updated_at ?? ''))], hubTpl)

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: latestDate(latestPost, templateDate('home')),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/articles`,
      lastModified: latestDate(latestPost, templateDate('articles')),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/strains`,
      lastModified: latestStrain,
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/strains/indica`,
      lastModified: latestStrainOfType('indica'),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/strains/sativa`,
      lastModified: latestStrainOfType('sativa'),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/strains/hybrid`,
      lastModified: latestStrainOfType('hybrid'),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/strains/compare`,
      lastModified: compareTpl,
      changeFrequency: 'weekly',
      priority: 0.6,
    },
    {
      url: `${baseUrl}/terpenes`,
      lastModified: templateDate('terpenes'),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    ...TERPENE_SLUGS.map((slug) => ({
      url: `${baseUrl}/terpenes/${slug}`,
      lastModified: templateDate('terpenes'),
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    })),
    {
      url: `${baseUrl}/videos`,
      lastModified: latestDate(latestPost, templateDate('videos')),
      changeFrequency: 'daily',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/topics`,
      lastModified: latestDate(latestPost, templateDate('topics')),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    // Topic hubs (hub-and-spoke into articles)
    ...topicClusters.map((c) => ({
      url: `${baseUrl}/topics/${c.id}`,
      lastModified: latestDate(maxDate(posts.filter((p) => matchesCluster(p, c)).map(postDate), latestPost), templateDate('topics')),
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    })),
    {
      url: `${baseUrl}/strains/a-z`,
      lastModified: latestStrain,
      changeFrequency: 'weekly',
      priority: 0.7,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: templateDate('about'),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${baseUrl}/contact`,
      lastModified: templateDate('contact'),
      changeFrequency: 'yearly',
      priority: 0.4,
    },
    {
      url: `${baseUrl}/privacy-policy`,
      lastModified: templateDate('privacy'),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/terms-of-service`,
      lastModified: templateDate('terms'),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/affiliate-disclosure`,
      lastModified: templateDate('affiliate'),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
  ]

  // Article pages — use last_updated when it exists and is newer than generated_at
  const articlePages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}/articles/${post.slug}`,
    lastModified: latestDate(postDate(post), templateDate('articles')),
    changeFrequency: 'weekly',
    priority: 0.8,
  }))

  // Strain pages — thin profiles (noindex,follow) are excluded so the sitemap
  // only lists URLs we actually want indexed.
  const strainPages: MetadataRoute.Sitemap = catalog
    .filter((s) => !isThinStrain(s))
    .map((s) => ({
      url: `${baseUrl}/strains/${s.slug}`,
      lastModified: latestDate(s.updated_at, strainTpl),
      changeFrequency: 'weekly',
      priority: 0.7,
    }))

  // Comparison pages: curated pairs + auto pairs (same set the strain pages
  // link to). lastmod = newest of the template and both strains' data.
  const updatedAt = new Map(catalog.map((s) => [s.slug, s.updated_at]))
  const comparisonPages: MetadataRoute.Sitemap = getAllComparisonPairs(catalog).map((p) => ({
    url: `${baseUrl}/strains/compare/${p.slug}`,
    lastModified: latestDate(compareTpl, updatedAt.get(p.a), updatedAt.get(p.b)),
    changeFrequency: 'monthly',
    priority: 0.5,
  }))

  // State pages: static data files, dated by their last git change.
  const statePages: MetadataRoute.Sitemap = [
    {
      url: `${baseUrl}/states`,
      lastModified: statesTpl,
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    {
      url: `${baseUrl}/states/compare`,
      lastModified: statesTpl,
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    ...statesData.map((s) => ({
      url: `${baseUrl}/states/${s.slug}`,
      lastModified: statesTpl,
      changeFrequency: 'monthly' as const,
      priority: 0.5,
    })),
  ]

  return [...staticPages, ...articlePages, ...strainPages, ...comparisonPages, ...statePages]
}
