import { getSortedPostsData } from '@/lib/posts'
import TopicsClient from './TopicsClient'
import { topicClusters, matchesCluster } from './topicClusters'

const baseUrl = 'https://strainreport.com'

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
        category: post.category,
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
      name: 'The Strain Report',
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
