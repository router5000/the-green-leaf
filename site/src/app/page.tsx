import { getSortedPostsData, getMonthlyPosts } from '@/lib/posts'
import HomeContent from '@/components/HomeContent'

export default function Home() {
  const allPosts = getSortedPostsData()
  const featuredPost = allPosts[0]
  const { posts: monthlyPosts, monthName } = getMonthlyPosts(3)
  const bottomPosts = allPosts.slice(4, 6)

  return (
    <div className="bg-gradient-to-b from-white to-gray-50 min-h-screen">
      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">

        {/* H1 for SEO - visually integrated with design */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-serif text-gray-900 mb-6 sm:mb-8 text-center">
          Cannabis Education & Guides
        </h1>
        <p className="text-gray-600 text-base sm:text-lg text-center max-w-2xl mx-auto mb-8 sm:mb-12">
          Accurate, balanced cannabis education. From strain guides and growing tips to health, wellness, and legal updates.
        </p>

        {allPosts.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200 shadow-sm">
            <p className="text-gray-700 text-lg mb-4">
              No articles yet. Generate your first batch of content!
            </p>
            <p className="text-gray-500">
              Run: <code className="bg-gray-100 px-3 py-1 rounded text-gray-700">python content_generator.py</code>
            </p>
          </div>
        ) : (
          <HomeContent
            featuredPost={featuredPost}
            bottomPosts={bottomPosts}
            monthlyPosts={monthlyPosts}
            monthName={monthName}
          />
        )}

      </div>
    </div>
  )
}
