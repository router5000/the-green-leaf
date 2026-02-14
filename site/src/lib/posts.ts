import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { remark } from 'remark'
import html from 'remark-html'
import { cache } from 'react'

const postsDirectory = path.join(process.cwd(), 'content/posts')

export interface VideoInsights {
  key_points?: string[]
  best_quote?: string
  pro_tips?: string[]
  seo_keywords?: string[]
  timestamp_topics?: string[]
}

export interface YouTubeVideo {
  id: string
  title: string
  channel: string
  position: 'hero' | 'section'
  thumbnail?: string
  relevance_score?: number
  insights?: VideoInsights
}

export interface FAQ {
  question: string
  answer: string
}

export interface HowToStep {
  name: string
  text: string
}

export interface HowToData {
  name: string
  steps: HowToStep[]
}

export interface TocItem {
  id: string
  text: string
  level: number
}

export interface PostData {
  slug: string
  title: string
  meta_description: string
  keyword: string
  featured_image?: string
  featured_image_alt?: string
  tags: string[]
  status: string
  generated_at: string
  season: string
  category?: string
  estimated_read_time: string
  word_count: number
  content?: string
  contentHtml?: string
  youtube?: YouTubeVideo[]
  faqs?: FAQ[]
  key_stat?: string
  tldr?: string
  last_updated?: string
  howTo?: HowToData
  toc?: TocItem[]
  sources?: { name: string; url: string }[]
}

export const getSortedPostsData = cache(function getSortedPostsData(): PostData[] {
  // Ensure directory exists
  if (!fs.existsSync(postsDirectory)) {
    fs.mkdirSync(postsDirectory, { recursive: true })
    return []
  }

  const fileNames = fs.readdirSync(postsDirectory)
  const allPostsData = fileNames
    .filter(fileName => fileName.endsWith('.md'))
    .map((fileName) => {
      const slug = fileName.replace(/\.md$/, '')
      const fullPath = path.join(postsDirectory, fileName)
      try {
        const fileContents = fs.readFileSync(fullPath, 'utf8')
        const matterResult = matter(fileContents)

        return {
          slug,
          ...(matterResult.data as Omit<PostData, 'slug'>),
        }
      } catch (error) {
        console.error(`Error reading post file ${fileName}:`, error)
        return null
      }
    })
    .filter((post): post is PostData => post !== null)

  // Sort by date
  return allPostsData.sort((a, b) => {
    if (a.generated_at < b.generated_at) {
      return 1
    } else {
      return -1
    }
  })
})

export function getAllPostSlugs() {
  if (!fs.existsSync(postsDirectory)) {
    return []
  }
  
  const fileNames = fs.readdirSync(postsDirectory)
  return fileNames
    .filter(fileName => fileName.endsWith('.md'))
    .map((fileName) => {
      return {
        params: {
          slug: fileName.replace(/\.md$/, ''),
        },
      }
    })
}

/**
 * Parse HowTo steps from markdown content.
 * Looks for H2 sections with "Step" or "How to" followed by H3 sub-steps.
 */
function cleanStepText(raw: string): string {
  return raw
    .replace(/\[\[\d+\]\]\(#user-content-fn-\d+\)/g, '')  // Remove footnote refs
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')              // Strip markdown links
    .replace(/  +/g, ' ')                                   // Collapse extra spaces
    .trim()
}

function parseHowToSteps(content: string, title: string): HowToData | undefined {
  const lines = content.split('\n')
  let inStepSection = false
  let sectionName = ''
  const steps: HowToStep[] = []
  let currentStep: { name: string; lines: string[] } | null = null

  for (const line of lines) {
    // Detect H2 "Step-by-Step" or "How to" sections
    const h2Match = line.match(/^## (.+)/)
    if (h2Match) {
      const heading = h2Match[1]
      if (/step.by.step|how to/i.test(heading)) {
        inStepSection = true
        sectionName = heading
        continue
      } else if (inStepSection) {
        // Exited the step section
        break
      }
    }

    if (!inStepSection) continue

    // Detect H3 steps within the section
    const h3Match = line.match(/^### (.+)/)
    if (h3Match) {
      if (currentStep) {
        const text = cleanStepText(currentStep.lines.join('\n'))
        if (text) steps.push({ name: currentStep.name, text })
      }
      currentStep = { name: h3Match[1].replace(/^Step \d+:\s*/i, ''), lines: [] }
      continue
    }

    // Collect content lines for current step
    if (currentStep && line.trim() && !line.startsWith('#')) {
      currentStep.lines.push(line.trim())
    }
  }

  // Push last step
  if (currentStep) {
    const text = cleanStepText(currentStep.lines.join('\n'))
    if (text) steps.push({ name: currentStep.name, text })
  }

  if (steps.length >= 2) {
    return { name: title, steps }
  }
  return undefined
}

export async function getPostData(slug: string): Promise<PostData> {
  const fullPath = path.join(postsDirectory, `${slug}.md`)

  if (!fs.existsSync(fullPath)) {
    throw new Error(`Post not found: ${slug}`)
  }

  const fileContents = fs.readFileSync(fullPath, 'utf8')
  const matterResult = matter(fileContents)

  // Remove H1 title from content (already displayed by page template)
  // Also removes the affiliate disclosure line that follows the H1
  let contentWithoutH1 = matterResult.content
    .replace(/^# .+\n+/m, '')  // Remove H1 line
    .replace(/^\*This article contains affiliate links\..+\*\n*/m, '')  // Remove affiliate disclosure

  // Replace YouTube shortcodes with HTML BEFORE markdown processing
  // Pattern: {{< youtube id="VIDEO_ID" title="TITLE" channel="CHANNEL" >}}
  const youtubePattern = /\{\{<\s*youtube\s+id="([^"]+)"\s+title="([^"]+)"\s+channel="([^"]+)"\s*>\}\}/g
  const contentWithVideos = contentWithoutH1.replace(youtubePattern, (match, id, title, channel) => {
    return `
<div class="youtube-embed my-8">
<div class="aspect-video rounded-xl overflow-hidden shadow-lg">
<iframe src="https://www.youtube.com/embed/${id}?rel=0" title="${title}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="w-full h-full"></iframe>
</div>
<p class="text-sm text-gray-500 mt-2 text-center">📺 ${title} • ${channel}</p>
</div>
`
  })

  // Convert markdown tables to HTML before remark processing
  const processCell = (cell: string): string => {
    // Convert markdown links [text](url) to <a> tags
    return cell.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, (_, text, url) => {
      const isAmazon = url.includes('amazon.com')
      const attrs = isAmazon
        ? ` target="_blank" rel="noopener noreferrer sponsored"`
        : ''
      return `<a href="${url}"${attrs}>${text}</a>`
    })
  }

  const contentWithTables = contentWithVideos.replace(
    /(?:^|\n)((?:\|.+\|[ \t]*\n)+)/g,
    (block) => {
      const lines = block.trim().split('\n').filter(l => l.trim())
      if (lines.length < 3) return block // Need header + separator + at least 1 row

      // Check for separator row (|---|---|)
      const sepIdx = lines.findIndex(l => /^\|[\s\-:|]+\|$/.test(l.trim()))
      if (sepIdx < 1) return block

      const parseRow = (line: string) =>
        line.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim())

      const headers = parseRow(lines[sepIdx - 1])
      const rows = lines.slice(sepIdx + 1).map(parseRow)

      let tableHtml = '\n<div class="overflow-x-auto my-6">\n<table class="comparison-table w-full">\n<thead><tr>'
      headers.forEach(h => { tableHtml += `<th class="px-6 py-3">${processCell(h)}</th>` })
      tableHtml += '</tr></thead>\n<tbody>\n'
      rows.forEach(row => {
        tableHtml += '<tr>'
        row.forEach(cell => { tableHtml += `<td class="px-6 py-3">${processCell(cell)}</td>` })
        tableHtml += '</tr>\n'
      })
      tableHtml += '</tbody>\n</table>\n</div>\n'
      return tableHtml
    }
  )

  // Process markdown to HTML (sanitize: false allows raw HTML like YouTube embeds)
  const processedContent = await remark()
    .use(html, { sanitize: false })
    .process(contentWithTables)
  let contentHtml = processedContent.toString()

  // Make Amazon affiliate links open in new tab
  // Pattern: <a href="https://www.amazon.com/...">
  contentHtml = contentHtml.replace(
    /<a href="(https:\/\/www\.amazon\.com[^"]*)">/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer sponsored">'
  )

  // Wrap Quick Answer section with semantic class for Speakable schema
  contentHtml = contentHtml.replace(
    /(<h2>Quick Answer<\/h2>\s*)([\s\S]*?)(?=<h2>)/,
    '<section class="quick-answer">$1$2</section>'
  )

  // Wrap Sources section with citation schema markup
  contentHtml = contentHtml.replace(
    /(<h2[^>]*>Sources<\/h2>)([\s\S]*)$/,
    '<section class="sources" itemScope itemType="https://schema.org/ItemList"><h2>Sources</h2><div itemProp="itemListElement">$2</div></section>'
  )

  // Optimize inline images with lazy loading and responsive sizing
  contentHtml = contentHtml.replace(
    /<img\s+([^>]*?)>/g,
    (match, attrs) => {
      if (attrs.includes('loading=')) return match
      return `<img ${attrs} loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, 720px">`
    }
  )

  // Add IDs to H2/H3 headings and extract TOC
  const toc: TocItem[] = []
  contentHtml = contentHtml.replace(/<(h[23])>(.*?)<\/\1>/g, (match, tag, text) => {
    const cleanText = text.replace(/<[^>]+>/g, '').trim()
    const id = cleanText.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
    const level = tag === 'h2' ? 2 : 3
    if (cleanText && !['Sources', 'Conclusion'].includes(cleanText)) {
      toc.push({ id, text: cleanText, level })
    }
    return `<${tag} id="${id}">${text}</${tag}>`
  })

  // Parse sources/citations from content
  const sources: { name: string; url: string }[] = []
  const sourcesSection = matterResult.content.match(/## Sources\s*([\s\S]*)$/)
  if (sourcesSection) {
    const sourceLinks = Array.from(sourcesSection[1].matchAll(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g))
    for (const match of sourceLinks) {
      sources.push({ name: match[1], url: match[2] })
    }
  }

  // Parse HowTo steps from content (for schema)
  const postData = matterResult.data as Omit<PostData, 'slug' | 'contentHtml' | 'content'>
  const howTo = parseHowToSteps(matterResult.content, postData.title || slug)

  return {
    slug,
    contentHtml,
    content: matterResult.content,
    ...postData,
    ...(howTo ? { howTo } : {}),
    ...(toc.length > 0 ? { toc } : {}),
    ...(sources.length > 0 ? { sources } : {}),
  }
}

export function getPostsByTag(tag: string): PostData[] {
  const allPosts = getSortedPostsData()
  return allPosts.filter(post => post.tags?.includes(tag))
}

export function getAllTags(): string[] {
  const allPosts = getSortedPostsData()
  const tagSet = new Set<string>()

  allPosts.forEach(post => {
    post.tags?.forEach(tag => tagSet.add(tag))
  })

  return Array.from(tagSet).sort()
}

export interface VideoWithArticle extends YouTubeVideo {
  articleSlug: string
  articleTitle: string
  articleImage?: string
  articleSeason: string
}

export function getAllVideos(): VideoWithArticle[] {
  const allPosts = getSortedPostsData()
  const videos: VideoWithArticle[] = []

  for (const post of allPosts) {
    if (post.youtube && post.youtube.length > 0) {
      for (const video of post.youtube) {
        videos.push({
          ...video,
          articleSlug: post.slug,
          articleTitle: post.title,
          articleImage: post.featured_image,
          articleSeason: post.season,
        })
      }
    }
  }

  return videos
}

// Month-to-season mapping for relevant content
const MONTH_CONFIG: Record<number, { seasons: string[], keywords: string[], name: string }> = {
  0:  { seasons: ['winter'], keywords: ['winter', 'snow', 'dormant', 'planning'], name: 'January' },
  1:  { seasons: ['winter', 'spring'], keywords: ['winter', 'prep', 'early spring', 'planning'], name: 'February' },
  2:  { seasons: ['spring'], keywords: ['spring', 'prep', 'fertilize', 'weed', 'seed'], name: 'March' },
  3:  { seasons: ['spring'], keywords: ['spring', 'fertilize', 'weed', 'mow', 'seed', 'aerate'], name: 'April' },
  4:  { seasons: ['spring', 'summer'], keywords: ['spring', 'mow', 'water', 'weed', 'growth'], name: 'May' },
  5:  { seasons: ['summer'], keywords: ['summer', 'water', 'mow', 'heat', 'drought'], name: 'June' },
  6:  { seasons: ['summer'], keywords: ['summer', 'water', 'heat', 'drought', 'pest'], name: 'July' },
  7:  { seasons: ['summer', 'fall'], keywords: ['summer', 'water', 'heat', 'prep', 'overseed'], name: 'August' },
  8:  { seasons: ['fall'], keywords: ['fall', 'overseed', 'aerate', 'fertilize', 'thatch'], name: 'September' },
  9:  { seasons: ['fall'], keywords: ['fall', 'leaves', 'fertilize', 'winterize', 'prep'], name: 'October' },
  10: { seasons: ['fall', 'winter'], keywords: ['fall', 'winter', 'winterize', 'leaves', 'prep'], name: 'November' },
  11: { seasons: ['winter'], keywords: ['winter', 'dormant', 'planning', 'equipment'], name: 'December' },
}

export function getMonthlyPosts(limit: number = 3): { posts: PostData[], monthName: string } {
  const now = new Date()
  const month = now.getMonth()
  const config = MONTH_CONFIG[month]

  const allPosts = getSortedPostsData()

  // Score posts by relevance to current month
  const scoredPosts = allPosts.map(post => {
    let score = 0

    // Season match (highest priority)
    if (config.seasons.includes(post.season?.toLowerCase())) {
      score += 10
    }

    // Keyword matches in title, keyword field, or tags
    const postText = `${post.title} ${post.keyword} ${post.tags?.join(' ')}`.toLowerCase()
    for (const keyword of config.keywords) {
      if (postText.includes(keyword)) {
        score += 3
      }
    }

    // Slight recency bonus for ties
    const daysOld = (now.getTime() - new Date(post.generated_at).getTime()) / (1000 * 60 * 60 * 24)
    score += Math.max(0, (365 - daysOld) / 365) // 0-1 bonus for recent posts

    return { post, score }
  })

  // Sort by score and return top N
  const topPosts = scoredPosts
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(item => item.post)

  return { posts: topPosts, monthName: config.name }
}

export function getRelatedPosts(currentSlug: string, limit: number = 2): PostData[] {
  const allPosts = getSortedPostsData()
  const currentPost = allPosts.find(post => post.slug === currentSlug)

  if (!currentPost) return []

  // Filter out current post
  const otherPosts = allPosts.filter(post => post.slug !== currentSlug)

  // Score each post by relevance
  const scoredPosts = otherPosts.map(post => {
    let score = 0

    // Same season bonus
    if (post.season === currentPost.season) {
      score += 3
    }

    // Shared tags bonus (most important)
    const sharedTags = post.tags?.filter(tag =>
      currentPost.tags?.includes(tag)
    ) || []
    score += sharedTags.length * 5

    // Keyword similarity (simple word matching)
    const currentKeywords = currentPost.keyword?.toLowerCase().split(' ') || []
    const postKeywords = post.keyword?.toLowerCase().split(' ') || []
    const sharedKeywords = currentKeywords.filter(word =>
      postKeywords.includes(word) && word.length > 3 // ignore small words
    )
    score += sharedKeywords.length * 2

    return { post, score }
  })

  // Sort by score (highest first) and return top N
  return scoredPosts
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(item => item.post)
}
