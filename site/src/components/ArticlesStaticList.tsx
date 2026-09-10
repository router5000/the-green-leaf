import Link from 'next/link'
import Image from 'next/image'
import type { PostData } from '@/lib/posts'
import { resolveArticleImage, resolveArticleImageAlt } from '@/lib/articleImage'

interface ArticlesStaticListProps {
  posts: PostData[]
}

/**
 * Server-rendered article inventory with real <a> links.
 * Used as the Suspense fallback for ArticlesTabs so crawlers / curl
 * still see every article href when useSearchParams forces the fallback.
 */
export default function ArticlesStaticList({ posts }: ArticlesStaticListProps) {
  if (posts.length === 0) {
    return (
      <div className="bg-leaf-50 rounded-lg p-8 text-center">
        <p className="text-leaf-700 text-lg">No articles published yet.</p>
      </div>
    )
  }

  return (
    <div>
      <nav aria-label="All published articles" className="space-y-8">
        {posts.map((post, index) => (
          <article
            key={post.slug}
            className="bg-white rounded-xl shadow-md overflow-hidden"
          >
            <div className="md:flex">
              <div className="md:w-80 md:flex-shrink-0">
                <div className="relative h-64 md:h-full min-h-[12rem] overflow-hidden">
                  <Image
                    src={resolveArticleImage(post, index)}
                    alt={resolveArticleImageAlt(post)}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 320px"
                  />
                </div>
              </div>

              <div className="p-6 flex-1">
                <div className="flex flex-wrap items-center gap-3 text-sm text-leaf-600 mb-3">
                  {post.tags?.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="bg-leaf-100 px-3 py-1 rounded-full font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                  {post.estimated_read_time && (
                    <span>{post.estimated_read_time}</span>
                  )}
                </div>

                <h2 className="text-2xl font-semibold text-leaf-900 mb-3">
                  <Link
                    href={`/articles/${post.slug}`}
                    className="hover:text-leaf-600 transition"
                  >
                    {post.title}
                  </Link>
                </h2>

                {post.meta_description && (
                  <p className="text-gray-600 mb-4">{post.meta_description}</p>
                )}

                <div className="flex items-center justify-end">
                  <Link
                    href={`/articles/${post.slug}`}
                    className="text-leaf-600 hover:text-leaf-800 font-medium text-sm whitespace-nowrap"
                    aria-label={`Read full article: ${post.title}`}
                  >
                    Read More →
                  </Link>
                </div>
              </div>
            </div>
          </article>
        ))}
      </nav>

      {/* Explicit crawlable index — plain anchors for every slug */}
      <ul className="sr-only" aria-label="Article URL index">
        {posts.map((post) => (
          <li key={`index-${post.slug}`}>
            <a href={`/articles/${post.slug}`}>{post.title}</a>
          </li>
        ))}
      </ul>
    </div>
  )
}
