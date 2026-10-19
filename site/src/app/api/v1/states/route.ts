import { statesData } from '@/data/statesData'
import { STATES_LAST_REVIEWED } from '@/data/statesContent'

export const dynamic = 'force-static'

export function GET() {
  return Response.json({
    lastReviewed: STATES_LAST_REVIEWED,
    note: 'General information, not legal advice. Laws change; verify with each official source.',
    states: statesData.map(s => ({ ...s, url: `https://strainreport.com/states/${s.slug}` })),
  }, { headers: { 'Access-Control-Allow-Origin': '*' } })
}
