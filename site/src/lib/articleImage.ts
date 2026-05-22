/**
 * Resolve the display image for an article card.
 *
 * Priority:
 *   1. Article's own featured_image
 *   2. Pick from the 12-image fallback pool using (index % 12) so adjacent
 *      cards in a list never share an image.
 */

const FALLBACK_POOL = Array.from({ length: 12 }, (_, i) =>
  `/images/fallbacks/fallback-${String(i + 1).padStart(2, '0')}.jpg`
)

export function resolveArticleImage(
  post: { slug: string; featured_image?: string | null; category?: string | null },
  index = 0
): string {
  if (post.featured_image) return post.featured_image
  return FALLBACK_POOL[index % FALLBACK_POOL.length]
}

export function resolveArticleImageAlt(post: {
  title: string
  featured_image?: string | null
  featured_image_alt?: string | null
}): string {
  if (post.featured_image && post.featured_image_alt) return post.featured_image_alt
  return post.title
}
