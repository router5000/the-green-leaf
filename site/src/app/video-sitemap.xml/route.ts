import { getSortedPostsData } from '@/lib/posts'

export async function GET() {
  const posts = getSortedPostsData()
  const baseUrl = 'https://strainreport.com'

  const urlEntries = posts
    .filter(post => post.youtube && post.youtube.length > 0)
    .map(post => {
      const videos = post.youtube!.map(video => {
        const thumbnailUrl = `https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`
        const playerUrl = `https://www.youtube.com/embed/${video.id}`
        const watchUrl = `https://www.youtube.com/watch?v=${video.id}`

        // Build description from insights if available
        let description = post.meta_description || ''
        if (video.insights?.key_points && video.insights.key_points.length > 0) {
          description = video.insights.key_points.slice(0, 2).join(' ')
        }

        return `
      <video:video>
        <video:thumbnail_loc>${escapeXml(thumbnailUrl)}</video:thumbnail_loc>
        <video:title>${escapeXml(video.title)}</video:title>
        <video:description>${escapeXml(description)}</video:description>
        <video:player_loc>${escapeXml(playerUrl)}</video:player_loc>
        <video:content_loc>${escapeXml(watchUrl)}</video:content_loc>
        <video:publication_date>${post.generated_at || post.last_updated || ''}</video:publication_date>
        <video:family_friendly>yes</video:family_friendly>
        <video:uploader info="${escapeXml(`https://www.youtube.com/@${video.channel.replace(/\s+/g, '')}`)}">${escapeXml(video.channel)}</video:uploader>
        <video:live>no</video:live>
      </video:video>`
      }).join('')

      return `
    <url>
      <loc>${baseUrl}/articles/${post.slug}</loc>${videos}
    </url>`
    })
    .join('')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">${urlEntries}
</urlset>`

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}

function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}
