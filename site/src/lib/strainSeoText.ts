/**
 * Pure, dependency-free builders for strain <title> and meta description.
 * (Self-contained so tests/strainSeoText.test.mjs can transpile it alone.)
 */

export const TITLE_MAX = 60
export const DESC_MIN = 140
export const DESC_MAX = 158

export type StrainSeoInput = {
  name: string
  strain_type: string | null
  thc_min?: number | null
  thc_max?: number | null
  short_description?: string | null
  effects?: { effect_name: string; effect_type: string }[] | null
  terpenes?: { terpene_name: string; percentage: number | null }[] | null
  flavors?: string[] | null
}

/**
 * "<Name> Strain: Effects, THC & Review (2026)", shortened for long names so
 * it stays within TITLE_MAX where possible. Always unique per strain name.
 */
export function buildStrainTitle(name: string, year = 2026): string {
  const n = name.trim()
  const variants = [
    `${n} Strain: Effects, THC & Review (${year})`,
    `${n} Strain: Effects & THC (${year})`,
    `${n} Strain Review (${year})`,
  ]
  return variants.find((t) => t.length <= TITLE_MAX) ?? variants[variants.length - 1]
}

function range(min: number | null | undefined, max: number | null | undefined): string | null {
  const lo = min ?? null
  const hi = max ?? null
  if (lo == null && hi == null) return null
  if (lo == null || hi == null || lo === hi) return `${lo ?? hi}%`
  return `${Math.min(lo, hi)}-${Math.max(lo, hi)}%`
}

function list(items: string[]): string {
  if (items.length <= 1) return items.join('')
  return `${items.slice(0, -1).join(', ')} and ${items[items.length - 1]}`
}

/** Cut at a word boundary (never mid-word), drop dangling punctuation/joiners. */
export function truncateAtWord(text: string, max: number): string {
  const t = text.replace(/\s+/g, ' ').trim()
  if (t.length <= max) return t
  let cut = t.slice(0, max + 1)
  const sp = cut.lastIndexOf(' ')
  cut = sp > 0 ? cut.slice(0, sp) : t.slice(0, max)
  cut = cut.replace(/[\s,;:–—-]+$/, '').replace(/\s+(and|or|with|of|the|a|an|to|in|for|by)$/i, '')
  return cut.replace(/[\s,;:–—-]+$/, '')
}

function firstSentence(s: string | null | undefined): string | null {
  if (!s?.trim()) return null
  const t = s.replace(/\s+/g, ' ').trim()
  const m = t.match(/^.*?[.!?](?=\s|$)/)
  return (m ? m[0] : t).trim()
}

const ensurePeriod = (s: string) => (/[.!?]$/.test(s) ? s : `${s}.`)

/**
 * Data-driven description of DESC_MIN–DESC_MAX chars that ends on a whole
 * word/sentence. Built from whole sentences (lead, THC, effects, terpenes,
 * flavors) packed greedily, then a closing call-to-action sized to fit.
 */
export function buildStrainDescription(d: StrainSeoInput): string {
  const name = d.name.trim()
  const type = (d.strain_type ?? '').toLowerCase()
  const typeWord = type ? `${type} ` : ''
  const article = /^[aeiou]/.test(typeWord || 'cannabis') ? 'an' : 'a'
  const thc = range(d.thc_min, d.thc_max)
  const effects = (d.effects ?? [])
    .filter((e) => e.effect_type === 'positive')
    .map((e) => e.effect_name.toLowerCase())
    .slice(0, 3)
  const terps = [...(d.terpenes ?? [])]
    .sort((a, b) => (b.percentage ?? 0) - (a.percentage ?? 0))
    .map((t) => t.terpene_name.toLowerCase())
    .slice(0, 2)
  const flavors = (d.flavors ?? []).map((f) => f.toLowerCase()).slice(0, 3)

  const lead = firstSentence(d.short_description)
  const dataLead = `${name} is ${article} ${typeWord}cannabis strain${thc ? ` with ${thc} THC` : ''}.`
  const sentences: string[] = []
  if (lead && lead.length <= DESC_MAX - 20) {
    sentences.push(ensurePeriod(lead))
    if (thc) sentences.push(`THC: ${thc}.`)
  } else {
    sentences.push(dataLead)
  }
  if (effects.length) sentences.push(`Effects: ${list(effects)}.`)
  if (terps.length) sentences.push(`Top terpenes: ${list(terps)}.`)
  if (flavors.length) sentences.push(`Tastes ${list(flavors)}.`)
  if (!lead || lead.length > DESC_MAX - 20) {
    // Long lead didn't fit as a sentence: offer a word-safe excerpt as filler.
    const ex = lead ? truncateAtWord(lead.replace(/[.!?]$/, ''), 90) : null
    if (ex && ex.split(' ').length > 4) sentences.push(`${ex}.`)
  }

  let out = ''
  for (const s of sentences) {
    const next = out ? `${out} ${s}` : s
    if (next.length <= DESC_MAX) out = next
  }
  if (!out) out = `${truncateAtWord(sentences[0], DESC_MAX - 1).replace(/[.!?]$/, '')}.`

  // Sparse profiles: add generic-but-true context sentences before the CTA.
  const typeNote: Record<string, string> = {
    indica: 'Indicas are usually relaxing and body-focused.',
    sativa: 'Sativas are usually uplifting and cerebral.',
    hybrid: 'Hybrids blend indica and sativa traits.',
  }
  const extras = [
    ...(sentences[0] === dataLead ? [] : [dataLead]),
    ...(typeNote[type] ? [typeNote[type]] : []),
  ]
  for (const s of extras) {
    if (out.length >= DESC_MIN - 20) break
    const next = `${out} ${s}`
    if (next.length <= DESC_MAX) out = next
  }

  const ctas = [
    'Read our full review with effects, THC, terpenes, flavors and grow info.',
    'Read our full review with effects, terpenes and grow info.',
    'Full review, effects, terpenes and grow tips.',
    'Read the full review and grow info.',
    'Read the full review.',
    'Full review inside.',
    'Read the review.',
    'Review inside.',
  ]
  if (out.length < DESC_MIN) {
    const cta = ctas.find((c) => out.length + 1 + c.length <= DESC_MAX)
    if (cta) out = `${out} ${cta}`
  }
  return out
}
