'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { motion } from 'framer-motion'

interface PostSummary {
  slug: string
  title: string
  season: string
  estimated_read_time: string
  category?: string
}

interface ClusterData {
  id: string
  title: string
  description: string
  icon: string
  color: string
  posts: PostSummary[]
}

// Map cluster IDs to their category images
const categoryImages: Record<string, string> = {
  'strains-genetics': '/images/topics/strains-genetics.jpg',
  'growing-cultivation': '/images/topics/growing-cultivation.jpg',
  'consumption-methods': '/images/topics/consumption-methods.jpg',
  'health-wellness': '/images/topics/health-wellness.jpg',
  'legal-industry': '/images/topics/legal-industry.jpg',
  'culture-lifestyle': '/images/topics/culture-lifestyle.jpg',
}

export default function TopicsClient({ clusters }: { clusters: ClusterData[] }) {
  const [activeCluster, setActiveCluster] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-b from-leaf-50 to-white">
      {/* Header */}
      <div className="bg-leaf-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <nav className="text-sm mb-4">
            <Link href="/" className="text-leaf-300 hover:text-white">Home</Link>
            <span className="mx-2 text-leaf-500">/</span>
            <span className="text-white">Topics</span>
          </nav>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Cannabis Topics
          </h1>
          <p className="text-xl text-leaf-200 max-w-2xl">
            Explore our comprehensive guides organized by topic. Whether you&apos;re growing your first plant,
            exploring new strains, or learning about wellness benefits, we&apos;ve got you covered.
          </p>
        </div>
      </div>

      {/* Topic Grid */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clusters.map((cluster, index) => (
            <motion.div
              key={cluster.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <div
                className={`relative rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 ${
                  activeCluster === cluster.id ? 'ring-2 ring-leaf-500 shadow-xl' : 'hover:shadow-lg'
                }`}
                onClick={() => setActiveCluster(activeCluster === cluster.id ? null : cluster.id)}
              >
                {/* Card Header with Image */}
                <div className={`bg-gradient-to-br ${cluster.color} p-[2px] pb-0 text-white`}>
                  {/* Inset Image Container - 2px border from top, right, left */}
                  <div className="relative w-full h-32 rounded-t-xl overflow-hidden">
                    <Image
                      src={categoryImages[cluster.id] || '/images/default-cannabis-hero.jpg'}
                      alt={cluster.title}
                      fill
                      className="object-cover"
                      sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    />
                  </div>
                  {/* Card Content */}
                  <div className="p-6 pt-4">
                    <h2 className="text-xl font-bold mb-2">{cluster.title}</h2>
                    <p className="text-sm text-white/80">{cluster.description}</p>
                    <div className="mt-4 flex items-center justify-between">
                      <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
                        {cluster.posts.length} articles
                      </span>
                      <span className="text-white/80">
                        {activeCluster === cluster.id ? '▲' : '▼'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Expanded Article List */}
                {activeCluster === cluster.id && cluster.posts.length > 0 && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-white border-t"
                  >
                    <div className="p-4 max-h-80 overflow-y-auto">
                      {cluster.posts.map((post) => (
                        <Link
                          key={post.slug}
                          href={`/articles/${post.slug}`}
                          className="block p-3 rounded-lg hover:bg-leaf-50 transition-colors mb-2 last:mb-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <h3 className="font-medium text-leaf-900 text-sm line-clamp-2">
                            {post.title}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">{cluster.title}</span>
                            <span className="text-xs text-gray-400">•</span>
                            <span className="text-xs text-gray-500">{post.estimated_read_time}</span>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* SEO Content Section */}
        <div className="mt-16 prose prose-leaf max-w-none">
          <h2 className="text-2xl font-bold text-leaf-900 mb-6">
            Your Complete Cannabis Resource
          </h2>
          <div className="grid md:grid-cols-2 gap-8 text-gray-700">
            <div>
              <h3 className="text-lg font-semibold text-leaf-800 mb-3">Strain Knowledge</h3>
              <p>
                From classic indica and sativa varieties to modern hybrids, our strain guides cover
                terpene profiles, effects, growing characteristics, and honest reviews to help you
                find the perfect strain for your needs.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-leaf-800 mb-3">Growing Expertise</h3>
              <p>
                Whether you&apos;re setting up your first grow tent or optimizing an outdoor garden,
                our cultivation guides cover everything from germination to harvest with
                step-by-step instructions.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-leaf-800 mb-3">Health & Wellness</h3>
              <p>
                Explore the science behind CBD, medical cannabis, and wellness applications.
                Our research-backed guides cover pain relief, anxiety, sleep, and more with
                citations from peer-reviewed studies.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-leaf-800 mb-3">Stay Legal & Informed</h3>
              <p>
                Cannabis laws change frequently. Our legal guides track state-by-state regulations,
                legalization updates, and industry developments to keep you informed and compliant.
              </p>
            </div>
          </div>
        </div>

        {/* Browse All CTA */}
        <div className="mt-12 text-center">
          <Link
            href="/articles"
            className="inline-flex items-center gap-2 bg-leaf-600 text-white px-8 py-3 rounded-full font-medium hover:bg-leaf-700 transition-colors"
          >
            Browse All Articles
            <span>→</span>
          </Link>
        </div>
      </div>
    </div>
  )
}
