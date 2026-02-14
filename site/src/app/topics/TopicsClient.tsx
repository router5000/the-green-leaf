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
  'seasonal-care': '/images/categories/seasonal-care.jpg',
  'lawn-health': '/images/categories/lawn-health.jpg',
  'weed-control': '/images/categories/weed-control.jpg',
  'lawn-problems': '/images/categories/lawn-problems.jpg',
  'equipment': '/images/categories/equipment.jpg',
  'grass-types': '/images/categories/grass-types.jpg',
}

export default function TopicsClient({ clusters }: { clusters: ClusterData[] }) {
  const [activeCluster, setActiveCluster] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-b from-grass-50 to-white">
      {/* Header */}
      <div className="bg-grass-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <nav className="text-sm mb-4">
            <Link href="/" className="text-grass-300 hover:text-white">Home</Link>
            <span className="mx-2 text-grass-500">/</span>
            <span className="text-white">Topics</span>
          </nav>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Lawn Care Topics
          </h1>
          <p className="text-xl text-grass-200 max-w-2xl">
            Explore our comprehensive guides organized by topic. Whether you&apos;re battling weeds,
            preparing for a new season, or troubleshooting lawn problems, we&apos;ve got you covered.
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
                  activeCluster === cluster.id ? 'ring-2 ring-grass-500 shadow-xl' : 'hover:shadow-lg'
                }`}
                onClick={() => setActiveCluster(activeCluster === cluster.id ? null : cluster.id)}
              >
                {/* Card Header with Image */}
                <div className={`bg-gradient-to-br ${cluster.color} p-[2px] pb-0 text-white`}>
                  {/* Inset Image Container - 2px border from top, right, left */}
                  <div className="relative w-full h-32 rounded-t-xl overflow-hidden">
                    <Image
                      src={categoryImages[cluster.id] || '/images/default-lawn-hero.jpg'}
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
                          className="block p-3 rounded-lg hover:bg-grass-50 transition-colors mb-2 last:mb-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <h3 className="font-medium text-grass-900 text-sm line-clamp-2">
                            {post.title}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500 capitalize">{post.season}</span>
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
        <div className="mt-16 prose prose-grass max-w-none">
          <h2 className="text-2xl font-bold text-grass-900 mb-6">
            Your Complete Lawn Care Resource
          </h2>
          <div className="grid md:grid-cols-2 gap-8 text-gray-700">
            <div>
              <h3 className="text-lg font-semibold text-grass-800 mb-3">Seasonal Expertise</h3>
              <p>
                Every season brings unique challenges for your lawn. Our seasonal guides help you
                stay ahead with the right timing for fertilizing, aerating, overseeding, and more.
                From spring preparation to winter protection, we cover it all.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-grass-800 mb-3">Problem Solving</h3>
              <p>
                Brown spots? Persistent weeds? Fungal disease? Our troubleshooting guides help you
                identify lawn problems quickly and provide proven solutions. Get your lawn back to
                health with expert advice.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-grass-800 mb-3">Equipment Guides</h3>
              <p>
                The right tools make all the difference. Learn proper mowing techniques, discover
                robot mower options, and master your string trimmer with our comprehensive equipment guides.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-grass-800 mb-3">Grass Selection</h3>
              <p>
                Cool season or warm season? Overseeding or complete renovation? Our grass type guides
                help you choose the right grass for your climate and lifestyle, plus expert seeding tips.
              </p>
            </div>
          </div>
        </div>

        {/* Browse All CTA */}
        <div className="mt-12 text-center">
          <Link
            href="/articles"
            className="inline-flex items-center gap-2 bg-grass-600 text-white px-8 py-3 rounded-full font-medium hover:bg-grass-700 transition-colors"
          >
            Browse All Articles
            <span>→</span>
          </Link>
        </div>
      </div>
    </div>
  )
}
