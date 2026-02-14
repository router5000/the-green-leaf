import { getSortedPostsData } from '@/lib/posts'

export async function GET() {
  const posts = getSortedPostsData()
  const baseUrl = 'https://lawncare.center'

  const urlEntries = posts
    .filter(post => post.featured_image)
    .map(post => {
      const images: string[] = []

      // Add featured image
      if (post.featured_image) {
        const featuredImageUrl = post.featured_image.startsWith('http')
          ? post.featured_image
          : `${baseUrl}${post.featured_image}`

        images.push(`
      <image:image>
        <image:loc>${escapeXml(featuredImageUrl)}</image:loc>
        <image:title>${escapeXml(post.featured_image_alt || post.title)}</image:title>
        <image:caption>${escapeXml(post.meta_description || '')}</image:caption>
      </image:image>`)
      }

      // Add section image if exists (check for common pattern)
      const sectionImage = post.featured_image?.replace('.jpg', '-section.jpg')
      if (sectionImage) {
        const sectionImageUrl = sectionImage.startsWith('http')
          ? sectionImage
          : `${baseUrl}${sectionImage}`

        images.push(`
      <image:image>
        <image:loc>${escapeXml(sectionImageUrl)}</image:loc>
        <image:title>${escapeXml(`${post.title} - Detail View`)}</image:title>
      </image:image>`)
      }

      return `
    <url>
      <loc>${baseUrl}/articles/${post.slug}</loc>${images.join('')}
    </url>`
    })
    .join('')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">${urlEntries}
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
