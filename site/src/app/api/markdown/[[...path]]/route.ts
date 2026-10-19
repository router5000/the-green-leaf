import TurndownService from 'turndown'

export const dynamic = 'force-dynamic'
const BASE = 'https://strainreport.com'

function notFoundMd(path: string) {
  return `# Page not found\n\nThere is no page at \`${path}\` on The Strain Report.\n\n- Home: ${BASE}/\n- Site guide for agents: ${BASE}/llms.txt\n- Sitemap: ${BASE}/sitemap.xml\n- Search API: ${BASE}/api/v1/search?q=blue+dream\n`
}

function mdResponse(body: string, status: number, canonical: string, noindex: boolean) {
  const headers: Record<string, string> = {
    'Content-Type': 'text/markdown; charset=utf-8',
    Vary: 'Accept',
    Link: `<${canonical}>; rel="canonical"`,
    'Cache-Control': status === 200 ? 'public, s-maxage=3600, stale-while-revalidate=86400' : 'no-store',
    'X-Markdown-Tokens': String(Math.ceil(body.length / 4)),
  }
  if (noindex) headers['X-Robots-Tag'] = 'noindex, follow'
  return new Response(body, { status, headers })
}

export async function GET(req: Request, ctx: { params: Promise<{ path?: string[] }> }) {
  const url = new URL(req.url)
  const segs = (await ctx.params).path || []
  const mode = segs[0]
  let path = mode === '_md' || mode === '_neg' ? '/' + segs.slice(1).map(encodeURIComponent).join('/') : '/' + segs.map(encodeURIComponent).join('/')
  if (!path.startsWith('/') || path.startsWith('//') || path.startsWith('/api/')) path = '/'
  const isMdUrl = mode === '_md'
  const canonical = `${BASE}${path === '/' ? '' : path}`
  const origin = process.env.VERCEL_URL && process.env.VERCEL_ENV !== 'production'
    ? `https://${process.env.VERCEL_URL}` : url.origin

  let res: Response
  try {
    res = await fetch(`${origin}${path}`, {
      headers: { Accept: 'text/html', 'x-agent-md': '1', 'x-vercel-protection-bypass': process.env.VERCEL_AUTOMATION_BYPASS_SECRET || '' },
      redirect: 'follow',
    })
  } catch {
    return mdResponse(`# Temporarily unavailable\n\nTry ${canonical} in HTML.\n`, 502, canonical, true)
  }
  if (res.status === 404) return mdResponse(notFoundMd(path), 404, `${BASE}/`, true)
  if (!res.ok) return mdResponse(`# Error ${res.status}\n\nSee ${canonical}\n`, res.status, canonical, true)

  const html = await res.text()
  const title = (html.match(/<title>([^<]*)<\/title>/i)?.[1] || 'The Strain Report').replace(/&amp;/g, '&').replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"')
  const desc = html.match(/<meta name="description" content="([^"]*)"/i)?.[1] || ''
  let main = html.match(/<main[\s\S]*?<\/main>/i)?.[0] || html.match(/<body[\s\S]*?<\/body>/i)?.[0] || html
  main = main
    .replace(/<(script|style|noscript|svg|canvas|iframe|template)[\s\S]*?<\/\1>/gi, '')
    .replace(/<(nav|button|form)[\s\S]*?<\/\1>/gi, '')
  const td = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced', bulletListMarker: '-' })
  td.addRule('dropImages', { filter: ['img', 'picture', 'figure'], replacement: () => '' })
  let body = td.turndown(main)
    .replace(/\]\(\//g, `](${BASE}/`)
    .replace(/\n{3,}/g, '\n\n')
    .trim()
  const front = `---\ntitle: ${JSON.stringify(title)}\nurl: ${canonical}\n${desc ? `description: ${JSON.stringify(desc.replace(/&amp;/g, '&'))}\n` : ''}source: The Strain Report (strainreport.com)\n---\n\n`
  if (!body.startsWith('# ')) body = `# ${title.split(' | ')[0]}\n\n${body}`
  return mdResponse(front + body + '\n', 200, canonical, isMdUrl)
}
