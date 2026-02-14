import type { PostData, YouTubeVideo } from './posts'

export interface ArticleSearchResult extends PostData {
  matchType: 'article'
  relevanceScore: number
}

export interface VideoSearchResult {
  id: string
  title: string
  channel: string
  position: 'hero' | 'section'
  insights?: {
    key_points?: string[]
    best_quote?: string
    pro_tips?: string[]
  }
  articleSlug: string
  articleTitle: string
  articleImage?: string
  matchType: 'video'
  relevanceScore: number
}

export type SearchResult = ArticleSearchResult | VideoSearchResult

/**
 * Calculate relevance score based on where the match occurred
 */
function calculateArticleRelevance(post: PostData, terms: string[]): number {
  let score = 0
  const title = post.title.toLowerCase()
  const keyword = post.keyword?.toLowerCase() || ''
  const description = post.meta_description?.toLowerCase() || ''
  const tags = (post.tags || []).join(' ').toLowerCase()

  for (const term of terms) {
    // Title match is most important
    if (title.includes(term)) score += 10
    // Keyword match is very important
    if (keyword.includes(term)) score += 8
    // Tag match is important
    if (tags.includes(term)) score += 5
    // Description match is helpful
    if (description.includes(term)) score += 3
  }

  return score
}

/**
 * Calculate relevance score for video matches
 */
function calculateVideoRelevance(video: YouTubeVideo, terms: string[]): number {
  let score = 0
  const title = video.title.toLowerCase()
  const channel = video.channel.toLowerCase()
  const quote = video.insights?.best_quote?.toLowerCase() || ''
  const keyPoints = (video.insights?.key_points || []).join(' ').toLowerCase()
  const proTips = (video.insights?.pro_tips || []).join(' ').toLowerCase()

  for (const term of terms) {
    if (title.includes(term)) score += 10
    if (channel.includes(term)) score += 3
    if (quote.includes(term)) score += 5
    if (keyPoints.includes(term)) score += 4
    if (proTips.includes(term)) score += 4
  }

  return score
}

/**
 * Search articles by query
 */
export function searchArticles(posts: PostData[], query: string): ArticleSearchResult[] {
  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean)
  if (terms.length === 0) return []

  const results: ArticleSearchResult[] = []

  for (const post of posts) {
    const searchableText = [
      post.title,
      post.meta_description,
      post.keyword,
      post.season,
      ...(post.tags || [])
    ].join(' ').toLowerCase()

    // Check if all terms match
    const allTermsMatch = terms.every(term => searchableText.includes(term))

    if (allTermsMatch) {
      results.push({
        ...post,
        matchType: 'article',
        relevanceScore: calculateArticleRelevance(post, terms)
      })
    }
  }

  // Sort by relevance score (highest first)
  return results.sort((a, b) => b.relevanceScore - a.relevanceScore)
}

/**
 * Search videos within articles by query
 */
export function searchVideos(posts: PostData[], query: string): VideoSearchResult[] {
  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean)
  if (terms.length === 0) return []

  const results: VideoSearchResult[] = []

  for (const post of posts) {
    const videos = post.youtube || []

    for (const video of videos) {
      const searchableText = [
        video.title,
        video.channel,
        video.insights?.best_quote,
        ...(video.insights?.key_points || []),
        ...(video.insights?.pro_tips || [])
      ].filter(Boolean).join(' ').toLowerCase()

      // Check if all terms match
      const allTermsMatch = terms.every(term => searchableText.includes(term))

      if (allTermsMatch) {
        results.push({
          id: video.id,
          title: video.title,
          channel: video.channel,
          position: video.position,
          insights: video.insights,
          articleSlug: post.slug,
          articleTitle: post.title,
          articleImage: post.featured_image,
          matchType: 'video',
          relevanceScore: calculateVideoRelevance(video, terms)
        })
      }
    }
  }

  // Sort by relevance score (highest first)
  return results.sort((a, b) => b.relevanceScore - a.relevanceScore)
}

/**
 * Combined search across articles and videos
 */
export function search(posts: PostData[], query: string): {
  articles: ArticleSearchResult[]
  videos: VideoSearchResult[]
  totalCount: number
} {
  const articles = searchArticles(posts, query)
  const videos = searchVideos(posts, query)

  return {
    articles,
    videos,
    totalCount: articles.length + videos.length
  }
}

/**
 * Highlight matching terms in text
 */
export function highlightMatch(text: string, query: string): string {
  if (!query.trim()) return text

  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean)
  let result = text

  for (const term of terms) {
    const regex = new RegExp(`(${term})`, 'gi')
    result = result.replace(regex, '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>')
  }

  return result
}
