import { getSortedPostsData } from '@/lib/posts'

const SITE_URL = 'https://thegreenleaf.com'

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export async function GET() {
  const posts = getSortedPostsData()

  const items = posts.slice(0, 50).map((post) => {
    const pubDate = new Date(post.generated_at || post.last_updated || Date.now()).toUTCString()
    return `    <item>
      <title>${escapeXml(post.title)}</title>
      <link>${SITE_URL}/articles/${post.slug}</link>
      <guid isPermaLink="true">${SITE_URL}/articles/${post.slug}</guid>
      <description>${escapeXml(post.meta_description)}</description>
      <pubDate>${pubDate}</pubDate>
      <category>${escapeXml(post.category || post.season || 'Cannabis')}</category>
    </item>`
  })

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>The Green Leaf</title>
    <link>${SITE_URL}</link>
    <description>Expert cannabis tips, guides, and seasonal advice for the perfect cannabis.</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
${items.join('\n')}
  </channel>
</rss>`

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}
