import { getSortedPostsData, type PostData } from '@/lib/posts'
import { hasTerpeneHub } from '@/lib/terpenes'

export type ArticleStrainLink = {
  strainSlug: string
  strainName: string
  terpeneSlugs: string[]
}

/** Explicit overrides when slug heuristics would be wrong or incomplete. */
const EXPLICIT_ARTICLE_STRAIN: Record<
  string,
  { strainSlug: string; strainName: string; terpeneSlugs?: string[] }
> = {
  'blue-dream-strain-effects-review': {
    strainSlug: 'blue-dream',
    strainName: 'Blue Dream',
    terpeneSlugs: ['myrcene', 'pinene'],
  },
  'girl-scout-cookies-strain-profile': {
    strainSlug: 'girl-scout-cookies',
    strainName: 'Girl Scout Cookies',
    terpeneSlugs: ['caryophyllene', 'limonene'],
  },
  'gorilla-glue-4-strain-review': {
    strainSlug: 'gorilla-glue-4',
    strainName: 'Gorilla Glue #4',
    terpeneSlugs: ['caryophyllene', 'myrcene'],
  },
  'jack-herer-strain-guide': {
    strainSlug: 'jack-herer',
    strainName: 'Jack Herer',
    terpeneSlugs: ['terpinolene', 'pinene'],
  },
  'mac-1-strain-guide': {
    strainSlug: 'mac-1',
    strainName: 'MAC 1',
    terpeneSlugs: ['limonene', 'caryophyllene'],
  },
  'animal-cookies-strain-review': {
    strainSlug: 'animal-cookies',
    strainName: 'Animal Cookies',
    terpeneSlugs: ['caryophyllene', 'limonene'],
  },
}

function titleCaseSlug(slug: string): string {
  return slug
    .split('-')
    .map((part) => {
      if (/^\d+$/.test(part)) return part
      if (part.toLowerCase() === 'mac') return 'MAC'
      return part.charAt(0).toUpperCase() + part.slice(1)
    })
    .join(' ')
}

/**
 * Resolve the primary strain profile (and optional terpene hubs) for an article.
 * Prefer explicit map; otherwise derive from `*-strain-{review|profile|guide}` slugs.
 */
export function getStrainLinkForArticle(slug: string): ArticleStrainLink | null {
  const explicit = EXPLICIT_ARTICLE_STRAIN[slug]
  if (explicit) {
    return {
      strainSlug: explicit.strainSlug,
      strainName: explicit.strainName,
      terpeneSlugs: (explicit.terpeneSlugs ?? []).filter((t) => hasTerpeneHub(t)),
    }
  }

  const match = slug.match(/^(.+)-strain-(?:effects-)?(?:review|profile|guide)$/)
  if (!match) return null

  const strainSlug = match[1]
  return {
    strainSlug,
    strainName: titleCaseSlug(strainSlug),
    terpeneSlugs: [],
  }
}

/** Articles that point at a given strain slug (inverse of getStrainLinkForArticle). */
export function findArticlesForStrain(
  strainSlug: string,
): Pick<PostData, 'slug' | 'title' | 'meta_description'>[] {
  return getSortedPostsData()
    .map((post) => {
      const link = getStrainLinkForArticle(post.slug)
      if (!link || link.strainSlug !== strainSlug) return null
      return {
        slug: post.slug,
        title: post.title,
        meta_description: post.meta_description,
      }
    })
    .filter((p): p is Pick<PostData, 'slug' | 'title' | 'meta_description'> => p !== null)
}
