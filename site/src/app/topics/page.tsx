import { getSortedPostsData, PostData } from '@/lib/posts'
import TopicsClient from './TopicsClient'

const baseUrl = 'https://thegreenleaf.com'

// Define topic clusters with their associated tags/keywords
const topicClusters = [
  {
    id: 'strains-genetics',
    title: 'Strains & Genetics',
    description: 'Explore indica, sativa, and hybrid strains with detailed terpene profiles, effects, and growing characteristics.',
    icon: '🧬',
    color: 'from-emerald-500 to-green-600',
    keywords: ['strain', 'indica', 'sativa', 'hybrid', 'terpene', 'genetics', 'phenotype'],
    tags: ['cannabis strains', 'indica', 'sativa', 'hybrid', 'terpene profiles'],
  },
  {
    id: 'growing-cultivation',
    title: 'Growing & Cultivation',
    description: 'Master cannabis cultivation with guides on indoor, outdoor, hydroponic, and soil growing techniques.',
    icon: '🌱',
    color: 'from-green-500 to-emerald-600',
    keywords: ['grow', 'cultivat', 'indoor', 'outdoor', 'hydro', 'soil', 'nutrient', 'light', 'flower', 'veg'],
    tags: ['growing cannabis', 'indoor growing', 'outdoor growing', 'hydroponics', 'nutrients'],
  },
  {
    id: 'consumption-methods',
    title: 'Consumption Methods',
    description: 'Learn about different ways to consume cannabis including smoking, edibles, tinctures, vaping, and topicals.',
    icon: '💨',
    color: 'from-lime-500 to-green-600',
    keywords: ['smoke', 'vape', 'edible', 'tincture', 'topical', 'dab', 'concentrate', 'oil'],
    tags: ['edibles', 'vaping', 'tinctures', 'concentrates', 'topicals'],
  },
  {
    id: 'health-wellness',
    title: 'Health & Wellness',
    description: 'Discover the science behind CBD, medical cannabis, and cannabis wellness applications.',
    icon: '💚',
    color: 'from-amber-500 to-orange-600',
    keywords: ['cbd', 'medical', 'pain', 'anxiety', 'sleep', 'wellness', 'therapeutic', 'health'],
    tags: ['CBD', 'medical cannabis', 'wellness', 'pain relief', 'anxiety'],
  },
  {
    id: 'legal-industry',
    title: 'Legal & Industry',
    description: 'Stay informed on cannabis legalization, state laws, regulations, and industry developments.',
    icon: '⚖️',
    color: 'from-blue-500 to-indigo-600',
    keywords: ['legal', 'law', 'regulat', 'licens', 'dispens', 'state', 'federal', 'legislat'],
    tags: ['cannabis law', 'legalization', 'regulations', 'dispensary'],
  },
  {
    id: 'culture-lifestyle',
    title: 'Culture & Lifestyle',
    description: 'Explore cannabis culture, recipes, history, events, travel guides, and lifestyle content.',
    icon: '🌿',
    color: 'from-teal-500 to-cyan-600',
    keywords: ['histor', 'recipe', 'event', 'travel', 'accessor', 'culture', 'lifestyle', 'cook'],
    tags: ['cannabis culture', 'recipes', 'cannabis history', 'accessories'],
  },
]

interface TopicCluster {
  id: string
  title: string
  description: string
  icon: string
  color: string
  keywords: string[]
  tags: string[]
}

function matchesCluster(post: PostData, cluster: TopicCluster): boolean {
  const postText = `${post.title} ${post.keyword} ${post.tags?.join(' ')}`.toLowerCase()

  // Check if any keyword matches
  const keywordMatch = cluster.keywords.some(kw => postText.includes(kw.toLowerCase()))

  // Check if any tag matches
  const tagMatch = cluster.tags.some(tag =>
    post.tags?.some(postTag => postTag.toLowerCase().includes(tag.toLowerCase()))
  )

  return keywordMatch || tagMatch
}

export default function TopicsPage() {
  const allPosts = getSortedPostsData()

  // Group posts by cluster and serialize for client
  const clusterPosts = topicClusters.map(cluster => ({
    ...cluster,
    posts: allPosts
      .filter(post => matchesCluster(post, cluster))
      .map(post => ({
        slug: post.slug,
        title: post.title,
        season: post.season,
        estimated_read_time: post.estimated_read_time,
      }))
  }))

  // CollectionPage schema with ItemList for each topic cluster
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': `${baseUrl}/topics`,
    name: 'Cannabis Topics & Guides',
    description: 'Comprehensive cannabis guides organized by topic: strains, growing, consumption, health, legal, and culture.',
    url: `${baseUrl}/topics`,
    isPartOf: {
      '@type': 'WebSite',
      '@id': `${baseUrl}/#website`,
      url: baseUrl,
      name: 'The Green Leaf',
    },
    mainEntity: clusterPosts.map(cluster => ({
      '@type': 'ItemList',
      name: cluster.title,
      description: cluster.description,
      numberOfItems: cluster.posts.length,
      itemListElement: cluster.posts.map((post, idx) => ({
        '@type': 'ListItem',
        position: idx + 1,
        url: `${baseUrl}/articles/${post.slug}`,
        name: post.title,
      })),
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <TopicsClient clusters={clusterPosts} />
    </>
  )
}
