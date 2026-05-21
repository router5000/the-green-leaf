import type { PostData } from '@/lib/posts'

export interface TopicCluster {
  id: string
  title: string
  description: string
  icon: string
  color: string
  keywords: string[]
  tags: string[]
}

export const topicClusters: TopicCluster[] = [
  {
    id: 'strains-genetics',
    title: 'Strains & Genetics',
    description: 'Explore indica, sativa, and hybrid strains with detailed terpene profiles, effects, and growing characteristics.',
    icon: '🧬',
    color: '#3d5c30',
    keywords: ['strain', 'indica', 'sativa', 'hybrid', 'terpene', 'genetics', 'phenotype'],
    tags: ['cannabis strains', 'indica', 'sativa', 'hybrid', 'terpene profiles'],
  },
  {
    id: 'growing-cultivation',
    title: 'Growing & Cultivation',
    description: 'Master cannabis cultivation with guides on indoor, outdoor, hydroponic, and soil growing techniques.',
    icon: '🌱',
    color: '#7a5c3a',
    keywords: ['grow', 'cultivat', 'indoor', 'outdoor', 'hydro', 'soil', 'nutrient', 'light', 'flower', 'veg'],
    tags: ['growing cannabis', 'indoor growing', 'outdoor growing', 'hydroponics', 'nutrients'],
  },
  {
    id: 'consumption-methods',
    title: 'Consumption Methods',
    description: 'Learn about different ways to consume cannabis including smoking, edibles, tinctures, vaping, and topicals.',
    icon: '💨',
    color: '#3a5c6e',
    keywords: ['smoke', 'vape', 'edible', 'tincture', 'topical', 'dab', 'concentrate', 'oil'],
    tags: ['edibles', 'vaping', 'tinctures', 'concentrates', 'topicals'],
  },
  {
    id: 'health-wellness',
    title: 'Health & Wellness',
    description: 'Discover the science behind CBD, medical cannabis, and cannabis wellness applications.',
    icon: '💚',
    color: '#5a3a5c',
    keywords: ['cbd', 'medical', 'pain', 'anxiety', 'sleep', 'wellness', 'therapeutic', 'health'],
    tags: ['CBD', 'medical cannabis', 'wellness', 'pain relief', 'anxiety'],
  },
  {
    id: 'legal-industry',
    title: 'Legal & Industry',
    description: 'Stay informed on cannabis legalization, state laws, regulations, and industry developments.',
    icon: '⚖️',
    color: '#3e3e3e',
    keywords: ['legal', 'law', 'regulat', 'licens', 'dispens', 'state', 'federal', 'legislat'],
    tags: ['cannabis law', 'legalization', 'regulations', 'dispensary'],
  },
  {
    id: 'culture-lifestyle',
    title: 'Culture & Lifestyle',
    description: 'Explore cannabis culture, recipes, history, events, travel guides, and lifestyle content.',
    icon: '🌿',
    color: '#4a6e5a',
    keywords: ['histor', 'recipe', 'event', 'travel', 'accessor', 'culture', 'lifestyle', 'cook'],
    tags: ['cannabis culture', 'recipes', 'cannabis history', 'accessories'],
  },
]

export function matchesCluster(post: PostData, cluster: TopicCluster): boolean {
  if (post.category === cluster.id) return true
  const postText = `${post.title} ${post.keyword} ${post.tags?.join(' ')}`.toLowerCase()
  const keywordMatch = cluster.keywords.some(kw => postText.includes(kw.toLowerCase()))
  const tagMatch = cluster.tags.some(tag =>
    post.tags?.some(postTag => postTag.toLowerCase().includes(tag.toLowerCase()))
  )
  return keywordMatch || tagMatch
}
