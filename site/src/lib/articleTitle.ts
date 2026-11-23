const SITE = 'The Strain Report'
const SITE_SUFFIX = /\s*[-–—|]\s*The Strain Report\s*$/i

/** Document title for an article: one site suffix, never doubled. */
export function articleDocumentTitle(title: string): string {
  let base = title.trim()
  while (SITE_SUFFIX.test(base)) base = base.replace(SITE_SUFFIX, '').trim()
  return base ? `${base} - ${SITE}` : SITE
}
