import { MetadataRoute } from 'next'
import { getSortedPostsData } from '@/lib/posts'
import { getSupabase } from '@/lib/supabase'
import { COMPARISON_PAIRS } from '@/data/strainComparisonPairs'
import { TERPENE_SLUGS } from '@/lib/terpenes'
import { statesData } from '@/data/statesData'

const baseUrl = 'https://strainreport.com'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = getSortedPostsData()

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/articles`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/strains`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/strains/indica`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/strains/sativa`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/strains/hybrid`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/strains/compare`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.6,
    },
    {
      url: `${baseUrl}/terpenes`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    ...TERPENE_SLUGS.map((slug) => ({
      url: `${baseUrl}/terpenes/${slug}`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    })),
    {
      url: `${baseUrl}/videos`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/topics`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date('2025-12-01'),
      changeFrequency: 'monthly',
      priority: 0.7,
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
  const articlePages: MetadataRoute.Sitemap = posts.map((post) => {
    const gen = new Date(post.generated_at)
    const last = post.last_updated ? new Date(post.last_updated) : null
    const lastMod = last && last > gen ? last : gen
    return {
      url: `${baseUrl}/articles/${post.slug}`,
      lastModified: lastMod,
      changeFrequency: 'weekly',
      priority: 0.8,
    }
  })

  // Strain pages — fetched live from Supabase
  let strainPages: MetadataRoute.Sitemap = []
  try {
    const { data } = await getSupabase()
      .from('strains')
      .select('slug, updated_at')
      .eq('published', true)
    if (data) {
      strainPages = (data as { slug: string; updated_at: string }[]).map((s) => ({
        url: `${baseUrl}/strains/${s.slug}`,
        lastModified: new Date(s.updated_at),
        changeFrequency: 'weekly',
        priority: 0.7,
      }))
    }
  } catch {
    // env unavailable during build — sitemap regenerates on the next request
  }

  // Curated comparison pages
  const comparisonPages: MetadataRoute.Sitemap = COMPARISON_PAIRS.map(([a, b]) => ({
    url: `${baseUrl}/strains/compare/${a}-vs-${b}`,
    lastModified: new Date(),
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
