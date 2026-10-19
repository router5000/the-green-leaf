import { MetadataRoute } from 'next'
import { getSortedPostsData } from '@/lib/posts'
import { getStrainCatalogSafe, isThinStrain, STATIC_CONTENT_LASTMOD } from '@/lib/strainCatalog'
import { topicClusters, matchesCluster } from '@/app/topics/topicClusters'
import { COMPARISON_PAIRS } from '@/data/strainComparisonPairs'
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
  const maxDate = (dates: Date[], fallback = STATIC_CONTENT_LASTMOD) => {
    const valid = dates.filter((d) => !isNaN(d.getTime()))
    return valid.length ? new Date(Math.max(...valid.map((d) => d.getTime()))) : fallback
  }
  const latestPost = maxDate(posts.map(postDate))
  const latestStrain = maxDate(catalog.map((s) => new Date(s.updated_at ?? '')))
  const latestStrainOfType = (t: string) =>
    maxDate(catalog.filter((s) => s.strain_type === t).map((s) => new Date(s.updated_at ?? '')))

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: latestPost,
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/articles`,
      lastModified: latestPost,
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
      lastModified: STATIC_CONTENT_LASTMOD,
      changeFrequency: 'weekly',
      priority: 0.6,
    },
    {
      url: `${baseUrl}/terpenes`,
      lastModified: STATIC_CONTENT_LASTMOD,
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    ...TERPENE_SLUGS.map((slug) => ({
      url: `${baseUrl}/terpenes/${slug}`,
      lastModified: STATIC_CONTENT_LASTMOD,
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    })),
    {
      url: `${baseUrl}/videos`,
      lastModified: latestPost,
      changeFrequency: 'daily',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/topics`,
      lastModified: latestPost,
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    // Topic hubs (hub-and-spoke into articles)
    ...topicClusters.map((c) => ({
      url: `${baseUrl}/topics/${c.id}`,
      lastModified: maxDate(posts.filter((p) => matchesCluster(p, c)).map(postDate), latestPost),
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
      lastModified: new Date('2025-12-01'),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${baseUrl}/contact`,
      lastModified: new Date('2026-10-19'),
      changeFrequency: 'yearly',
      priority: 0.4,
    },
    {
      url: `${baseUrl}/privacy-policy`,
      lastModified: new Date('2025-12-01'),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/terms-of-service`,
      lastModified: new Date('2025-12-01'),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/affiliate-disclosure`,
      lastModified: new Date('2025-12-01'),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
  ]

  // Article pages — use last_updated when it exists and is newer than generated_at
  const articlePages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}/articles/${post.slug}`,
    lastModified: postDate(post),
    changeFrequency: 'weekly',
    priority: 0.8,
  }))

  // Strain pages — thin profiles (noindex,follow) are excluded so the sitemap
  // only lists URLs we actually want indexed.
  const strainPages: MetadataRoute.Sitemap = catalog
    .filter((s) => !isThinStrain(s))
    .map((s) => ({
      url: `${baseUrl}/strains/${s.slug}`,
      ...(s.updated_at ? { lastModified: new Date(s.updated_at) } : {}),
      changeFrequency: 'weekly',
      priority: 0.7,
    }))

  // Curated comparison pages
  const comparisonPages: MetadataRoute.Sitemap = COMPARISON_PAIRS.map(([a, b]) => ({
    url: `${baseUrl}/strains/compare/${a}-vs-${b}`,
    lastModified: STATIC_CONTENT_LASTMOD,
    changeFrequency: 'monthly',
    priority: 0.5,
  }))

  // State pages (static data, no lastmod source — omit rather than guess)
  const statePages: MetadataRoute.Sitemap = [
    {
      url: `${baseUrl}/states`,
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    ...statesData.map((s) => ({
      url: `${baseUrl}/states/${s.slug}`,
      changeFrequency: 'monthly' as const,
      priority: 0.5,
    })),
  ]

  return [...staticPages, ...articlePages, ...strainPages, ...comparisonPages, ...statePages]
}
