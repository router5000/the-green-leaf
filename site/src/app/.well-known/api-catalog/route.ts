export const dynamic = 'force-static'
const BASE = 'https://strainreport.com'

/** RFC 9727 API catalog (linkset). */
export function GET() {
  const body = {
    linkset: [
      {
        anchor: `${BASE}/api/v1/search`,
        'service-desc': [{ href: `${BASE}/openapi.json`, type: 'application/openapi+json' }],
        'service-doc': [{ href: `${BASE}/llms.txt`, type: 'text/markdown' }],
      },
      {
        anchor: `${BASE}/api/v1/states`,
        'service-desc': [{ href: `${BASE}/openapi.json`, type: 'application/openapi+json' }],
        'service-doc': [{ href: `${BASE}/llms.txt`, type: 'text/markdown' }],
      },
      {
        anchor: `${BASE}/states/cannabis-laws.csv`,
        'describedby': [{ href: `${BASE}/states/compare`, type: 'text/html' }],
        'service-doc': [{ href: `${BASE}/llms.txt`, type: 'text/markdown' }],
      },
    ],
  }
  return new Response(JSON.stringify(body, null, 2), {
    headers: { 'Content-Type': 'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"', 'Access-Control-Allow-Origin': '*' },
  })
}
