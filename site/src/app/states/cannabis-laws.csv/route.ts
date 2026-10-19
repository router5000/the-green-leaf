import { getCompareRows, rowsToCsv } from '@/data/statesCompare'

export const dynamic = 'force-static'

export function GET() {
  return new Response(rowsToCsv(getCompareRows()), {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'inline; filename="strainreport-cannabis-laws-by-state.csv"',
      'Access-Control-Allow-Origin': '*',
    },
  })
}
