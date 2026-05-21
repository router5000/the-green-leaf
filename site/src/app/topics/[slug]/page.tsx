import { notFound } from 'next/navigation'
import { getSortedPostsData } from '@/lib/posts'
import { topicClusters, matchesCluster } from '../topicClusters'
import CategoryDetailClient from './CategoryDetailClient'
import type { Metadata } from 'next'

const baseUrl = 'https://thegreenleaf.com'

export function generateStaticParams() {
  return topicClusters.map(c => ({ slug: c.id }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params
  const cluster = topicClusters.find(c => c.id === slug)
  if (!cluster) return {}
  return {
    title: `${cluster.title} - Cannabis Guides | The Green Leaf`,
    description: cluster.description,
    alternates: { canonical: `${baseUrl}/topics/${slug}` },
    openGraph: {
      title: `${cluster.title} - The Green Leaf`,
      description: cluster.description,
      url: `${baseUrl}/topics/${slug}`,
    },
  }
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const cluster = topicClusters.find(c => c.id === slug)
  if (!cluster) notFound()

  const allPosts = getSortedPostsData()
  const posts = allPosts
    .filter(p => matchesCluster(p, cluster))
    .map(p => ({
      slug: p.slug,
      title: p.title,
      meta_description: p.meta_description,
      featured_image: p.featured_image ?? null,
      featured_image_alt: p.featured_image_alt ?? null,
      tags: p.tags ?? [],
      estimated_read_time: p.estimated_read_time,
      category: p.category ?? null,
    }))

  return (
    <CategoryDetailClient
      cluster={{
        id: cluster.id,
        title: cluster.title,
        description: cluster.description,
        color: cluster.color,
      }}
      posts={posts}
    />
  )
}
