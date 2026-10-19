import { NextResponse, type NextRequest } from 'next/server'

/**
 * Markdown for Agents: requests that prefer text/markdown (or end in .md)
 * are rewritten to /api/markdown, which renders the same page as Markdown.
 * Browsers and search crawlers keep getting HTML; all responses carry
 * `Vary: Accept` so caches keep the two variants apart.
 */
function wantsMarkdown(accept: string): boolean {
  if (!accept.includes('text/markdown')) return false
  // Only when markdown is preferred over HTML (or HTML not requested).
  const parts = accept.split(',').map(p => p.trim())
  const q = (type: string) => {
    const p = parts.find(x => x.startsWith(type))
    if (!p) return -1
    const m = p.match(/;\s*q=([0-9.]+)/)
    return m ? parseFloat(m[1]) : 1
  }
  return q('text/markdown') >= q('text/html')
}

export function proxy(req: NextRequest) {
  if (req.headers.get('x-agent-md') === '1') return NextResponse.next()
  const { pathname } = req.nextUrl
  const isMdPath = pathname.endsWith('.md') && pathname !== '/.md'
  if (isMdPath || wantsMarkdown(req.headers.get('accept') || '')) {
    let target = isMdPath ? pathname.slice(0, -3) : pathname
    if (target === '/index' || target === '') target = '/'
    const url = req.nextUrl.clone()
    url.pathname = `/api/markdown/${isMdPath ? '_md' : '_neg'}${target === '/' ? '' : target}`
    url.search = ''
    return NextResponse.rewrite(url)
  }
  const res = NextResponse.next()
  res.headers.set('Vary', 'Accept')
  return res
}

export const config = {
  matcher: ['/((?!_next/|api/|.well-known/|favicon|images/|.*\\.(?:png|jpe?g|gif|svg|ico|webp|avif|xml|txt|json|js|css|map|woff2?)$).*)'],
}
