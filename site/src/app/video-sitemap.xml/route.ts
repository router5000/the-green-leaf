import { getSortedPostsData } from '@/lib/posts'

/** Google video sitemap: title ≤100, description ≤2048 chars. */
const TITLE_MAX = 100
const DESCRIPTION_MAX = 2048

export async function GET() {
  const posts = getSortedPostsData()
  const baseUrl = 'https://strainreport.com'

  const urlEntries = posts
    .filter(post => post.youtube && post.youtube.length > 0)
    .map(post => {
      const videos = post.youtube!.map(video => {
        const thumbnailUrl = `https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`
        const playerUrl = `https://www.youtube.com/embed/${video.id}`

        // Prefer insight key points; always keep a non-empty description for Google.
        let description = post.meta_description || ''
        if (video.insights?.key_points && video.insights.key_points.length > 0) {
          description = video.insights.key_points.slice(0, 2).join(' ')
        }
        const title = limitText(video.title || 'Video', TITLE_MAX)
        description = limitText(description || title, DESCRIPTION_MAX)

        const publicationDate = toW3CDate(post.generated_at || post.last_updated)
        const uploaderInfoUrl = youtubeUploaderInfoUrl(video.channel || '')
        const uploaderTag = uploaderInfoUrl
          ? `<video:uploader info="${escapeXml(uploaderInfoUrl)}">${escapeXml(video.channel || '')}</video:uploader>`
          : `<video:uploader>${escapeXml(video.channel || 'Unknown')}</video:uploader>`

        // YouTube embeds: use player_loc only. content_loc must be a direct media file URL,
        // not a youtube.com/watch page — invalid content_loc is a common GSC reject cause.
        return `
      <video:video>
        <video:thumbnail_loc>${escapeXml(thumbnailUrl)}</video:thumbnail_loc>
        <video:title>${escapeXml(title)}</video:title>
        <video:description>${escapeXml(description)}</video:description>
        <video:player_loc>${escapeXml(playerUrl)}</video:player_loc>
        <video:publication_date>${escapeXml(publicationDate)}</video:publication_date>
        <video:family_friendly>yes</video:family_friendly>
        ${uploaderTag}
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

function limitText(text: string, max: number): string {
  const trimmed = text.trim()
  if (trimmed.length <= max) return trimmed
  return trimmed.slice(0, max)
}

/** W3C Datetime with timezone (Z). Bare microsecond timestamps without offset are invalid for Google. */
function toW3CDate(value?: string): string {
  if (!value?.trim()) return new Date().toISOString()
  const raw = value.trim()
  const hasTz = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(raw)
  const parsed = new Date(hasTz ? raw : `${raw}Z`)
  if (Number.isNaN(parsed.getTime())) return new Date().toISOString()
  return parsed.toISOString()
}

/**
 * Build an ASCII-only YouTube @handle URL for video:uploader@info.
 * Emoji/trademark chars in channel names produce invalid/non-fetchable info URLs.
 */
function youtubeUploaderInfoUrl(channel: string): string | null {
  const handle = channel
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\x00-\x7F]/g, '')
    .replace(/\s+/g, '')
    .replace(/[^A-Za-z0-9_-]/g, '')
  if (!handle) return null
  return `https://www.youtube.com/@${handle}`
}
