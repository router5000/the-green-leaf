'use client'

import Link from 'next/link'
import Image from 'next/image'
import { motion } from 'framer-motion'
import type { PostData } from '@/lib/posts'
import { resolveArticleImage, resolveArticleImageAlt } from '@/lib/articleImage'

const CATEGORY_LABELS: Record<string, string> = {
  'strains-genetics': 'Strains & Genetics',
  'growing-cultivation': 'Growing & Cultivation',
  'consumption-methods': 'Consumption Methods',
  'health-wellness': 'Health & Wellness',
  'legal-industry': 'Legal & Industry',
  'culture-lifestyle': 'Culture & Lifestyle',
}

function formatCategory(category?: string): string {
  if (category && CATEGORY_LABELS[category]) return CATEGORY_LABELS[category]
  return category || 'Cannabis'
}

interface HomeContentProps {
  featuredPost: PostData | undefined
  bottomPosts: PostData[]
  monthlyPosts: PostData[]
  monthName: string
}

export default function HomeContent({ featuredPost, bottomPosts, monthlyPosts, monthName }: HomeContentProps) {
  return (
    <div className="space-y-14 lg:space-y-20">

      {/* ── 1. Featured article — editorial split ──────────────────── */}
      {featuredPost && (
        <motion.article
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Link href={`/articles/${featuredPost.slug}`} className="group block">
            <div className="grid lg:grid-cols-5 rounded-2xl overflow-hidden shadow-xl">

              {/* Image panel — 3 columns */}
              <div className="lg:col-span-3 relative h-72 sm:h-96 lg:h-[500px] bg-gradient-to-br from-emerald-100 via-teal-50 to-emerald-100">
                <Image
                  src={resolveArticleImage(featuredPost, 0)}
                  alt={resolveArticleImageAlt(featuredPost)}
                  fill
                  className="object-cover group-hover:scale-105 transition-transform duration-700"
                  sizes="(max-width: 1024px) 100vw, 60vw"
                  priority
                />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/10 pointer-events-none" />
              </div>

              {/* Text panel — 2 columns, dark editorial */}
              <div className="lg:col-span-2 bg-gray-950 text-white flex flex-col justify-center px-8 py-10 lg:px-10 lg:py-12">
                <div className="flex items-center gap-2 text-xs text-gray-500 uppercase tracking-widest mb-5">
                  <span className="text-leaf-400 font-medium">{formatCategory(featuredPost.category)}</span>
                  <span>·</span>
                  <span>
                    {new Date(featuredPost.generated_at).toLocaleDateString('en-US', {
                      month: 'short', day: 'numeric', year: 'numeric',
                    })}
                  </span>
                </div>

                <h2 className="font-serif text-2xl sm:text-3xl lg:text-4xl leading-tight mb-5 group-hover:text-leaf-300 transition-colors duration-300">
                  {featuredPost.title}
                </h2>

                <p className="text-gray-400 text-sm leading-relaxed mb-8 line-clamp-3">
                  {featuredPost.meta_description}
                </p>

                <span className="inline-flex items-center gap-2 text-sm font-medium text-leaf-400 group-hover:text-leaf-300 transition-colors">
                  Read article
                  <svg
                    className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </span>
              </div>
            </div>
          </Link>
        </motion.article>
      )}

      {/* ── 3. Latest articles ─────────────────────────────────────── */}
      {bottomPosts.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm uppercase tracking-widest text-gray-900 font-semibold">Latest</h2>
            <Link href="/articles" className="text-xs text-leaf-600 hover:text-leaf-800 transition-colors">
              View all →
            </Link>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {bottomPosts.map((post, index) => (
              <motion.article
                key={post.slug}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 + index * 0.1 }}
              >
                <Link href={`/articles/${post.slug}`} className="group block">
                  <div className="relative h-56 mb-4 overflow-hidden rounded-xl bg-gradient-to-br from-leaf-100 via-emerald-50 to-teal-100 shadow-md">
                    <Image
                      src={resolveArticleImage(post, index + 1)}
                      alt={resolveArticleImageAlt(post)}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-700"
                      sizes="(max-width: 768px) 100vw, 50vw"
                    />
                    <div
                      className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                      style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.4), rgba(227,191,112,0.4))' }}
                    />
                    <div className="absolute top-3 left-3">
                      <span className="inline-block px-3 py-1 bg-white/90 backdrop-blur-sm text-xs font-medium text-gray-700 rounded-full shadow-sm">
                        {formatCategory(post.category)}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs text-gray-400">
                      {new Date(post.generated_at).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', year: 'numeric',
                      })}
                    </p>
                    <h3 className="text-xl font-serif text-gray-900 leading-tight group-hover:text-leaf-700 transition-colors line-clamp-2">
                      {post.title}
                    </h3>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </section>
      )}

      {/* ── 4. Monthly recommendations ─────────────────────────────── */}
      {monthlyPosts.length > 0 && (
        <section className="pb-4">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-sm uppercase tracking-widest text-gray-900 font-semibold">
                Things to Know in {monthName}
              </h2>
              <p className="text-xs text-gray-400 mt-1">Curated reads for this month</p>
            </div>
            <Link href="/articles?tab=monthly" className="text-xs text-leaf-600 hover:text-leaf-800 transition-colors">
              View all →
            </Link>
          </div>

          <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {monthlyPosts.map((post, index) => (
              <motion.article
                key={post.slug}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
              >
                <Link href={`/articles/${post.slug}`} className="group block">
                  <div className="relative h-44 mb-4 overflow-hidden rounded-lg bg-gradient-to-br from-leaf-100 via-emerald-50 to-teal-100 shadow-md">
                    <Image
                      src={resolveArticleImage(post, index + 3)}
                      alt={resolveArticleImageAlt(post)}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-700"
                      sizes="(max-width: 1024px) 100vw, 33vw"
                    />
                    <div
                      className="absolute inset-0 opacity-100 group-hover:opacity-0 transition-opacity duration-700 pointer-events-none"
                      style={{ background: 'linear-gradient(45deg, rgba(92,116,86,0.4), rgba(227,191,112,0.4))' }}
                    />
                  </div>

                  <div className="space-y-1">
                    <p className="text-xs text-leaf-600 uppercase tracking-wide font-medium">
                      {formatCategory(post.category)}
                    </p>
                    <h4 className="text-base font-serif text-gray-900 leading-tight group-hover:text-leaf-700 transition-colors line-clamp-2">
                      {post.title}
                    </h4>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </section>
      )}

    </div>
  )
}
