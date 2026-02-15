'use client'

import Link from 'next/link'
import Image from 'next/image'
import { motion } from 'framer-motion'
import type { PostData } from '@/lib/posts'

interface HomeContentProps {
  featuredPost: PostData | undefined
  bottomPosts: PostData[]
  monthlyPosts: PostData[]
  monthName: string
}

export default function HomeContent({ featuredPost, bottomPosts, monthlyPosts, monthName }: HomeContentProps) {
  return (
    <div className="grid lg:grid-cols-3 gap-8 lg:gap-12">

      {/* Left Column - Featured + Bottom Articles */}
      <div className="lg:col-span-2 space-y-8 lg:space-y-12">

        {/* Featured Article (Large) */}
        {featuredPost && (
          <motion.article
            className="group"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Link href={`/articles/${featuredPost.slug}`}>
              {/* Hero image */}
              <div className="relative h-[300px] sm:h-[400px] lg:h-[500px] mb-6 overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-100 via-teal-50 to-emerald-100 shadow-lg">
                {featuredPost.featured_image ? (
                  <>
                    <Image
                      src={featuredPost.featured_image}
                      alt={featuredPost.featured_image_alt || featuredPost.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-700"
                      sizes="(max-width: 1024px) 100vw, 66vw"
                      priority
                    />
                    <div
                      className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                      style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.5), rgba(227,191,112,0.5))' }}
                    />
                  </>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-32 h-32 rounded-full bg-leaf-300 opacity-60"></div>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 text-sm text-gray-500 uppercase tracking-wide">
                  <span>{new Date(featuredPost.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  <span>IN</span>
                  <span className="text-leaf-600">{featuredPost.season.toUpperCase()}</span>
                </div>

                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif text-gray-900 leading-tight group-hover:text-leaf-700 transition">
                  {featuredPost.title}
                </h2>

                <p className="text-gray-600 text-lg leading-relaxed max-w-3xl">
                  {featuredPost.meta_description}
                </p>
              </div>
            </Link>
          </motion.article>
        )}

        {/* Bottom Two Articles (Smaller) */}
        {bottomPosts.length > 0 && (
          <div className="grid md:grid-cols-2 gap-6 md:gap-8 pt-6 md:pt-8 border-t border-gray-200">
            {bottomPosts.map((post, index) => (
              <motion.article
                key={post.slug}
                className="group"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              >
                <Link href={`/articles/${post.slug}`}>
                  {/* Article image */}
                  <div className="relative h-64 mb-4 overflow-hidden rounded-xl bg-gradient-to-br from-leaf-100 via-emerald-50 to-teal-100 shadow-md">
                    {post.featured_image ? (
                      <>
                        <Image
                          src={post.featured_image}
                          alt={post.featured_image_alt || post.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-700"
                          sizes="(max-width: 768px) 100vw, 33vw"
                        />
                        <div
                          className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                          style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.5), rgba(227,191,112,0.5))' }}
                        />
                      </>
                    ) : (
                      <div className="absolute top-4 left-4 w-16 h-16 rounded-full bg-leaf-300 opacity-40"></div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-xs text-gray-500 uppercase tracking-wide">
                      <span>{new Date(post.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                      <span>IN</span>
                      <span className="text-leaf-600">{post.season.toUpperCase()}</span>
                    </div>

                    <h3 className="text-2xl font-serif text-gray-900 leading-tight group-hover:text-leaf-700 transition line-clamp-3">
                      {post.title}
                    </h3>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        )}

      </div>

      {/* Right Sidebar - Monthly Recommendations */}
      <motion.div
        className="lg:col-span-1"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="sticky top-8">
          <Link href="/articles?tab=monthly" className="flex items-center justify-between mb-8 group">
            <h3 className="text-sm uppercase tracking-widest text-gray-900 font-semibold group-hover:text-leaf-700 transition">Things to Know in {monthName}</h3>
            <span className="text-leaf-600 group-hover:text-leaf-800 transition">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </Link>

          <div className="space-y-8">
            {monthlyPosts.map((post, index) => (
              <motion.article
                key={post.slug}
                className="group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
              >
                <Link href={`/articles/${post.slug}`} className="block">
                  {/* Sidebar thumbnail */}
                  <div className="relative h-48 mb-4 overflow-hidden rounded-lg bg-gradient-to-br from-leaf-100 via-emerald-50 to-teal-100 shadow-md">
                    {post.featured_image ? (
                      <>
                        <Image
                          src={post.featured_image}
                          alt={post.featured_image_alt || post.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-700"
                          sizes="(max-width: 1024px) 100vw, 33vw"
                        />
                        <div
                          className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                          style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.5), rgba(227,191,112,0.5))' }}
                        />
                      </>
                    ) : (
                      <div className="absolute bottom-4 right-4 w-12 h-12 rounded-full bg-leaf-300 opacity-50"></div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <h4 className="text-lg font-serif text-gray-900 leading-tight group-hover:text-leaf-700 transition line-clamp-2">
                      {post.title}
                    </h4>
                    <p className="text-xs text-leaf-600 uppercase tracking-wide font-medium">
                      {post.season.toUpperCase()}
                    </p>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </motion.div>

    </div>
  )
}
