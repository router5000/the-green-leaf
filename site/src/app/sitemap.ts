import { MetadataRoute } from 'next'
import { getSortedPostsData } from '@/lib/posts'
import { getSupabase } from '@/lib/supabase'

const baseUrl = 'https://strainreport.com'

// Curated list of popular strain comparisons. Expand based on real traffic.
const COMPARISON_PAIRS: [string, string][] = [
  ['blue-dream',         'og-kush'],
  ['sour-diesel',        'blue-dream'],
  ['og-kush',            'girl-scout-cookies'],
  ['granddaddy-purple',  'northern-lights'],
  ['wedding-cake',       'gelato'],
  ['pineapple-express',  'sour-diesel'],
  ['gorilla-glue',       'og-kush'],
  ['white-widow',        'ak-47'],
  ['jack-herer',         'sour-diesel'],
  ['bubba-kush',         'afghan-kush'],
  ['green-crack',        'sour-diesel'],
  ['purple-haze',        'amnesia-haze'],
  ['chemdawg',           'og-kush'],
  ['trainwreck',         'jack-herer'],
  ['northern-lights',    'bubba-kush'],
]

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

  // Article pages
  const articlePages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}/articles/${post.slug}`,
    lastModified: new Date(post.generated_at),
    changeFrequency: 'weekly',
    priority: 0.8,
  }))

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

  return [...staticPages, ...articlePages, ...strainPages, ...comparisonPages]
}
