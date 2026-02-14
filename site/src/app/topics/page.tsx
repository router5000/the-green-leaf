import { getSortedPostsData, PostData } from '@/lib/posts'
import TopicsClient from './TopicsClient'

const baseUrl = 'https://lawncare.center'

// Define topic clusters with their associated tags/keywords
const topicClusters = [
  {
    id: 'seasonal-care',
    title: 'Seasonal Lawn Care',
    description: 'Master your lawn care routine for every season with expert timing guides and seasonal checklists.',
    icon: '🗓️',
    color: 'from-emerald-500 to-green-600',
    keywords: ['spring', 'summer', 'fall', 'winter', 'seasonal', 'preparation'],
    tags: ['spring lawn care', 'fall lawn care', 'winter lawn care', 'seasonal lawn care'],
  },
  {
    id: 'lawn-health',
    title: 'Lawn Health & Maintenance',
    description: 'Keep your lawn thriving with proper fertilizing, aerating, dethatching, and watering techniques.',
    icon: '🌱',
    color: 'from-green-500 to-emerald-600',
    keywords: ['fertiliz', 'aerat', 'dethatch', 'water', 'health', 'maintenance'],
    tags: ['fertilizing', 'lawn aeration', 'dethatching', 'lawn watering', 'soil health'],
  },
  {
    id: 'weed-control',
    title: 'Weed Control',
    description: 'Identify and eliminate lawn weeds with proven strategies for crabgrass, spurge, and more.',
    icon: '🌿',
    color: 'from-lime-500 to-green-600',
    keywords: ['weed', 'crabgrass', 'spurge', 'pre-emergent', 'post-emergent', 'herbicide'],
    tags: ['weed control', 'pre-emergent', 'post-emergent', 'crabgrass'],
  },
  {
    id: 'lawn-problems',
    title: 'Lawn Problems & Solutions',
    description: 'Diagnose and fix common lawn issues including brown spots, disease, fungus, and more.',
    icon: '🔧',
    color: 'from-amber-500 to-orange-600',
    keywords: ['problem', 'disease', 'fungus', 'fungicide', 'yellow', 'dead', 'brown', 'spot', 'bumpy'],
    tags: ['lawn problems', 'disease prevention', 'fungicide'],
  },
  {
    id: 'equipment',
    title: 'Equipment & Techniques',
    description: 'Get the most from your lawn care tools with expert mowing, trimming, and equipment guides.',
    icon: '🔨',
    color: 'from-blue-500 to-indigo-600',
    keywords: ['mow', 'trimmer', 'mower', 'robot', 'equipment', 'tool', 'scalp'],
    tags: ['lawn mowing', 'grass care'],
  },
  {
    id: 'grass-types',
    title: 'Grass Types & Seeding',
    description: 'Choose the right grass and master overseeding techniques for a lush, healthy lawn.',
    icon: '🌾',
    color: 'from-teal-500 to-cyan-600',
    keywords: ['seed', 'overseed', 'grass type', 'cool season', 'warm season', 'dallas', 'identification'],
    tags: ['grass seed', 'overseeding', 'cool season grass', 'warm season grass'],
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
    name: 'Lawn Care Topics & Guides',
    description: 'Comprehensive lawn care guides organized by topic: seasonal care, weed control, lawn health, equipment, grass types, and problem solving.',
    url: `${baseUrl}/topics`,
    isPartOf: {
      '@type': 'WebSite',
      '@id': `${baseUrl}/#website`,
      url: baseUrl,
      name: 'Lawn Care Center',
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
