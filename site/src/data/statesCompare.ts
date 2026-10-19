import { statesData, type StateData } from '@/data/statesData'
import { STATES_LAST_REVIEWED } from '@/data/statesContent'

/** Display tier for the comparison table. Derived from verified data only:
 *  Texas (Compassionate Use, low-THC) and Iowa (Medical Cannabidiol) run
 *  restricted low-THC programs rather than full medical markets. */
export type StatusTier = 'recreational' | 'medical' | 'cbd-only' | 'illegal'

const LOW_THC_ONLY = new Set(['texas', 'iowa'])

export const TIER_LABEL: Record<StatusTier, string> = {
  recreational: 'Recreational',
  medical: 'Medical',
  'cbd-only': 'Low-THC / CBD only',
  illegal: 'Illegal',
}

export const TIER_BADGE: Record<StatusTier, string> = {
  recreational: 'bg-leaf-100 text-leaf-700',
  medical: 'bg-amber-100 text-amber-700',
  'cbd-only': 'bg-sky-100 text-sky-700',
  illegal: 'bg-red-100 text-red-600',
}

export const TIER_ORDER: Record<StatusTier, number> = { recreational: 0, medical: 1, 'cbd-only': 2, illegal: 3 }

export interface CompareRow {
  slug: string
  name: string
  tier: StatusTier
  possessionLimit: string
  homeGrow: string
  minimumAge: number | null
  salesOpen: boolean
  publicUse: string
  lastReviewed: string
  url: string
  officialLink: string
}

export function tierFor(s: StateData): StatusTier {
  if (LOW_THC_ONLY.has(s.slug)) return 'cbd-only'
  return s.legalStatus
}

export function getCompareRows(): CompareRow[] {
  return statesData.map(s => ({
    slug: s.slug,
    name: s.name,
    tier: tierFor(s),
    possessionLimit: s.possessionLimit,
    homeGrow: s.homeGrow,
    minimumAge: s.legalStatus === 'illegal' ? null : s.purchaseAge,
    salesOpen: s.dispensaries,
    publicUse: s.consumptionNote,
    lastReviewed: STATES_LAST_REVIEWED,
    url: `https://strainreport.com/states/${s.slug}`,
    officialLink: s.officialLink,
  }))
}

/** FAQs built only from fields already on the page (no new claims). */
export function getStateFaqs(s: StateData): { q: string; a: string }[] {
  const tier = tierFor(s)
  const faqs: { q: string; a: string }[] = []
  const statusAnswer =
    tier === 'recreational'
      ? `Yes. Adult-use (recreational) cannabis is legal in ${s.name} for adults ${s.purchaseAge} and older. Possession limit: ${s.possessionLimit}.`
      : tier === 'medical'
      ? `Only for registered medical patients. ${s.name} has a medical cannabis program, but adult-use cannabis is not legal. Possession limit: ${s.possessionLimit}.`
      : tier === 'cbd-only'
      ? `Only in a restricted form. ${s.name} allows a limited low-THC program for registered patients; other cannabis remains illegal. Limit: ${s.possessionLimit}.`
      : `No. Cannabis is illegal in ${s.name}. ${s.penalties}`
  faqs.push({ q: `Is cannabis legal in ${s.name}?`, a: statusAnswer.trim() })
  faqs.push({ q: `Can you grow cannabis at home in ${s.name}?`, a: `${s.homeGrow}.`.replace(/\.\.$/, '.') })
  if (tier !== 'illegal') {
    faqs.push({
      q: `How old do you have to be to buy cannabis in ${s.name}?`,
      a: tier === 'recreational'
        ? `The minimum age for adult-use purchases in ${s.name} is ${s.purchaseAge}.`
        : `${s.name}'s program lists a minimum age of ${s.purchaseAge} for patients.`,
    })
    faqs.push({
      q: `Are dispensaries open in ${s.name}?`,
      a: s.dispensaries
        ? `Yes. Licensed dispensaries are operating in ${s.name}${tier === 'recreational' ? '' : ' for registered patients'}.`
        : `Not yet. There are no licensed ${tier === 'recreational' ? 'adult-use stores' : 'dispensaries'} operating in ${s.name} at the time of our last review.`,
    })
  }
  faqs.push({ q: `Can you use cannabis in public in ${s.name}?`, a: s.consumptionNote })
  return faqs
}

export function rowsToCsv(rows: CompareRow[]): string {
  const head = ['state', 'slug', 'status', 'possession_limit', 'home_grow', 'minimum_age', 'dispensary_sales_open', 'public_use', 'last_reviewed', 'page_url', 'official_source']
  const esc = (v: unknown) => {
    const s = v === null || v === undefined ? '' : String(v)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const lines = rows.map(r => [r.name, r.slug, TIER_LABEL[r.tier], r.possessionLimit, r.homeGrow, r.minimumAge ?? '', r.salesOpen ? 'yes' : 'no', r.publicUse, r.lastReviewed, r.url, r.officialLink].map(esc).join(','))
  return [head.join(','), ...lines].join('\n') + '\n'
}
