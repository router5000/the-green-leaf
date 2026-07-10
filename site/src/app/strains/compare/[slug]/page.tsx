import { getSupabase } from '@/lib/supabase'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import CompareAnotherStrain from '@/components/CompareAnotherStrain'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

const TYPE_BADGE: Record<string, string> = {
  indica: 'bg-purple-100 text-purple-700',
  sativa: 'bg-green-100 text-green-700',
  hybrid: 'bg-orange-100 text-orange-600',
}

const DIFFICULTY_BADGE: Record<string, string> = {
  easy:      'bg-green-100 text-green-700',
  moderate:  'bg-amber-100 text-amber-700',
  difficult: 'bg-red-100 text-red-600',
}

const SLEEP_KEYWORDS = ['sleep', 'sedat', 'relax', 'calm', 'drows', 'tranquil']

// ── Types ──────────────────────────────────────────────────────────────────

type Effect  = { id: string; effect_name: string; effect_type: string; intensity: number | null }
type Terpene = { id: string; terpene_name: string; percentage: number | null }

type Strain = {
  id: string
  name: string
  slug: string
  strain_type: string
  thc_min: number | null
  thc_max: number | null
  cbd_min: number | null
  cbd_max: number | null
  description: string | null
  short_description: string | null
  flavors: string[] | null
  difficulty: string | null
  flowering_time_days: number | null
  yield_indoor: string | null
  yield_outdoor: string | null
  effects: Effect[]
  terpenes: Terpene[]
}

// ── Helpers ────────────────────────────────────────────────────────────────

function parseSlugPair(slug: string): [string, string] | null {
  const parts = slug.split('-vs-')
  if (parts.length !== 2) return null
  const [a, b] = parts
  if (!a || !b || a === b) return null
  return [a, b]
}

function parseYieldMax(s: string | null): number | null {
  if (!s) return null
  const range = s.match(/(\d+)\s*[-–]\s*(\d+)/)
  if (range) return Number(range[2])
  const single = s.match(/(\d+)/)
  return single ? Number(single[1]) : null
}

function topEffects(effects: Effect[], n = 3): Effect[] {
  return effects
    .filter((e) => e.effect_type === 'positive' || e.effect_type === 'medical')
    .sort((a, b) => (b.intensity ?? 0) - (a.intensity ?? 0))
    .slice(0, n)
}

function topTerpenes(terpenes: Terpene[], n = 3): Terpene[] {
  return [...terpenes]
    .sort((a, b) => (b.percentage ?? 0) - (a.percentage ?? 0))
    .slice(0, n)
}

function sleepScore(effects: Effect[]): number {
  return effects.filter((e) =>
    SLEEP_KEYWORDS.some((kw) => e.effect_name.toLowerCase().includes(kw)),
  ).length
}

async function fetchPair(slugA: string, slugB: string): Promise<[Strain, Strain] | null> {
  try {
    const { data } = await getSupabase()
      .from('strains')
      .select('id, name, slug, strain_type, thc_min, thc_max, cbd_min, cbd_max, description, short_description, flavors, difficulty, flowering_time_days, yield_indoor, yield_outdoor, effects(*), terpenes(*)')
      .in('slug', [slugA, slugB])
      .eq('published', true)
    if (!data || data.length !== 2) return null
    const items = data as unknown as Strain[]
    const a = items.find((s) => s.slug === slugA)
    const b = items.find((s) => s.slug === slugB)
    if (!a || !b) return null
    return [a, b]
  } catch {
    return null
  }
}

// ── Metadata ───────────────────────────────────────────────────────────────

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const pair = parseSlugPair(slug)
  if (!pair) return {}
  const fetched = await fetchPair(pair[0], pair[1])
  if (!fetched) return {}
  const [a, b] = fetched
  const title = `${a.name} vs ${b.name} — Cannabis Strain Comparison | The Strain Report`
  const description = `Side-by-side comparison of ${a.name} and ${b.name}: THC%, CBD%, effects, terpenes, growing info, and more.`
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `${baseUrl}/strains/compare/${slug}`,
      siteName: 'The Strain Report',
      type: 'website',
    },
    twitter: { card: 'summary_large_image', title, description },
    alternates: { canonical: `${baseUrl}/strains/compare/${slug}` },
  }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function CompareStrainsPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const pair = parseSlugPair(slug)
  if (!pair) notFound()

  const fetched = await fetchPair(pair[0], pair[1])
  if (!fetched) notFound()
  const [a, b] = fetched

  // Load all strain slugs/names for the autocomplete footer
  let allSlugs: { slug: string; name: string }[] = []
  try {
    const { data } = await getSupabase()
      .from('strains')
      .select('slug, name')
      .eq('published', true)
      .order('name')
    allSlugs = (data as { slug: string; name: string }[]) ?? []
  } catch {
    // env unavailable
  }

  // Winner calculations
  const thcWinner = winner(a.thc_max, b.thc_max)
  const cbdWinner = winner(a.cbd_max, b.cbd_max)
  const yieldIndoorWinner  = winner(parseYieldMax(a.yield_indoor),  parseYieldMax(b.yield_indoor))
  const yieldOutdoorWinner = winner(parseYieldMax(a.yield_outdoor), parseYieldMax(b.yield_outdoor))

  // FAQ answers
  const strongerAnswer = thcWinner === 'a'
    ? `${a.name} is generally stronger with THC up to ${a.thc_max}%, compared to ${b.name} at ${b.thc_max}%.`
    : thcWinner === 'b'
      ? `${b.name} is generally stronger with THC up to ${b.thc_max}%, compared to ${a.name} at ${a.thc_max}%.`
      : `Both ${a.name} and ${b.name} have comparable THC levels.`

  const differenceAnswer = `${a.name} is a ${a.strain_type} strain${
    topEffects(a.effects).length ? ` known for ${topEffects(a.effects).slice(0, 2).map((e) => e.effect_name).join(' and ')}` : ''
  }, while ${b.name} is a ${b.strain_type} strain${
    topEffects(b.effects).length ? ` known for ${topEffects(b.effects).slice(0, 2).map((e) => e.effect_name).join(' and ')}` : ''
  }.`

  const sleepA = sleepScore(a.effects)
  const sleepB = sleepScore(b.effects)
  const sleepAnswer = sleepA === 0 && sleepB === 0
    ? `Neither ${a.name} nor ${b.name} is specifically known for sleep effects.`
    : sleepA > sleepB
      ? `${a.name} is better for sleep — its profile includes more sedating effects than ${b.name}.`
      : sleepB > sleepA
        ? `${b.name} is better for sleep — its profile includes more sedating effects than ${a.name}.`
        : `Both ${a.name} and ${b.name} contain sedating effects in similar measure.`

  // JSON-LD
  const strainSchemaA = buildStrainSchema(a)
  const strainSchemaB = buildStrainSchema(b)
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      { '@type': 'Question', name: `Is ${a.name} stronger than ${b.name}?`, acceptedAnswer: { '@type': 'Answer', text: strongerAnswer } },
      { '@type': 'Question', name: `What is the difference between ${a.name} and ${b.name}?`, acceptedAnswer: { '@type': 'Answer', text: differenceAnswer } },
      { '@type': 'Question', name: `Which is better for sleep, ${a.name} or ${b.name}?`, acceptedAnswer: { '@type': 'Answer', text: sleepAnswer } },
    ],
  }
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home',    item: baseUrl },
      { '@type': 'ListItem', position: 2, name: 'Strains', item: `${baseUrl}/strains` },
      { '@type': 'ListItem', position: 3, name: 'Compare', item: `${baseUrl}/strains/compare/${slug}` },
      { '@type': 'ListItem', position: 4, name: `${a.name} vs ${b.name}` },
    ],
  }

  return (
    <div className="min-h-screen bg-[#f0f0f0]">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(strainSchemaA) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(strainSchemaB) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />

      <div className="px-4 sm:px-6 md:px-[160px] pt-10 pb-16">
        {/* Breadcrumb */}
        <nav className="text-sm text-gray-500 mb-6" aria-label="Breadcrumb">
          <ol className="flex flex-wrap items-center gap-1.5">
            <li><Link href="/" className="hover:text-leaf-700 no-underline">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/strains" className="hover:text-leaf-700 no-underline">Strains</Link></li>
            <li aria-hidden="true">/</li>
            <li><span className="text-gray-700 font-medium">Compare</span></li>
            <li aria-hidden="true">/</li>
            <li><span className="text-gray-700 font-medium">{a.name} vs {b.name}</span></li>
          </ol>
        </nav>

        <h1 className="font-serif text-4xl md:text-5xl text-gray-900 mb-2">
          {a.name} <span className="text-gray-400">vs</span> {b.name}
        </h1>
        <p className="text-gray-500 mb-10">
          Side-by-side comparison: THC, CBD, effects, terpenes, growing info.
        </p>

        {/* Comparison table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <CompareTable
            a={a}
            b={b}
            thcWinner={thcWinner}
            cbdWinner={cbdWinner}
            yieldIndoorWinner={yieldIndoorWinner}
            yieldOutdoorWinner={yieldOutdoorWinner}
          />
        </div>

        {/* Compare another strain */}
        <CompareAnotherStrain
          slugs={allSlugs}
          currentSlugA={a.slug}
          currentSlugB={b.slug}
        />
      </div>
    </div>
  )
}

// ── Comparison table ───────────────────────────────────────────────────────

function CompareTable({
  a, b,
  thcWinner, cbdWinner, yieldIndoorWinner, yieldOutdoorWinner,
}: {
  a: Strain
  b: Strain
  thcWinner: 'a' | 'b' | null
  cbdWinner: 'a' | 'b' | null
  yieldIndoorWinner:  'a' | 'b' | null
  yieldOutdoorWinner: 'a' | 'b' | null
}) {
  const rows: { label: string; cellA: React.ReactNode; cellB: React.ReactNode }[] = [
    {
      label: 'Type',
      cellA: <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${TYPE_BADGE[a.strain_type] ?? 'bg-gray-100 text-gray-600'}`}>{a.strain_type}</span>,
      cellB: <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${TYPE_BADGE[b.strain_type] ?? 'bg-gray-100 text-gray-600'}`}>{b.strain_type}</span>,
    },
    {
      label: 'THC',
      cellA: <ValueCell value={range(a.thc_min, a.thc_max, '%')} winner={thcWinner === 'a'} />,
      cellB: <ValueCell value={range(b.thc_min, b.thc_max, '%')} winner={thcWinner === 'b'} />,
    },
    {
      label: 'CBD',
      cellA: <ValueCell value={range(a.cbd_min, a.cbd_max, '%')} winner={cbdWinner === 'a'} />,
      cellB: <ValueCell value={range(b.cbd_min, b.cbd_max, '%')} winner={cbdWinner === 'b'} />,
    },
    {
      label: 'Top effects',
      cellA: <ChipList items={topEffects(a.effects).map((e) => e.effect_name)} />,
      cellB: <ChipList items={topEffects(b.effects).map((e) => e.effect_name)} />,
    },
    {
      label: 'Top terpenes',
      cellA: <ChipList items={topTerpenes(a.terpenes).map((t) => t.terpene_name)} />,
      cellB: <ChipList items={topTerpenes(b.terpenes).map((t) => t.terpene_name)} />,
    },
    {
      label: 'Flowering time',
      cellA: <ValueCell value={a.flowering_time_days ? `${a.flowering_time_days} days` : '—'} winner={false} />,
      cellB: <ValueCell value={b.flowering_time_days ? `${b.flowering_time_days} days` : '—'} winner={false} />,
    },
    {
      label: 'Yield (indoor)',
      cellA: <ValueCell value={a.yield_indoor ?? '—'} winner={yieldIndoorWinner === 'a'} />,
      cellB: <ValueCell value={b.yield_indoor ?? '—'} winner={yieldIndoorWinner === 'b'} />,
    },
    {
      label: 'Yield (outdoor)',
      cellA: <ValueCell value={a.yield_outdoor ?? '—'} winner={yieldOutdoorWinner === 'a'} />,
      cellB: <ValueCell value={b.yield_outdoor ?? '—'} winner={yieldOutdoorWinner === 'b'} />,
    },
    {
      label: 'Difficulty',
      cellA: a.difficulty
        ? <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${DIFFICULTY_BADGE[a.difficulty] ?? 'bg-gray-100 text-gray-600'}`}>{a.difficulty}</span>
        : <span className="text-gray-400">—</span>,
      cellB: b.difficulty
        ? <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${DIFFICULTY_BADGE[b.difficulty] ?? 'bg-gray-100 text-gray-600'}`}>{b.difficulty}</span>
        : <span className="text-gray-400">—</span>,
    },
    {
      label: 'Flavors',
      cellA: <ChipList items={(a.flavors ?? []).slice(0, 3)} />,
      cellB: <ChipList items={(b.flavors ?? []).slice(0, 3)} />,
    },
  ]

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="bg-gray-50 border-b border-gray-200">
          <th className="text-left text-xs uppercase tracking-wide text-gray-400 px-4 py-3 font-medium w-1/4"> </th>
          <th className="text-left text-base text-gray-900 px-4 py-3 font-semibold">
            <Link href={`/strains/${a.slug}`} className="hover:text-leaf-700 no-underline">{a.name}</Link>
          </th>
          <th className="text-left text-base text-gray-900 px-4 py-3 font-semibold">
            <Link href={`/strains/${b.slug}`} className="hover:text-leaf-700 no-underline">{b.name}</Link>
          </th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={r.label} className={i % 2 ? 'bg-gray-50/40' : 'bg-white'}>
            <td className="px-4 py-3 text-xs uppercase tracking-wide text-gray-400 align-top">{r.label}</td>
            <td className="px-4 py-3 align-top">{r.cellA}</td>
            <td className="px-4 py-3 align-top">{r.cellB}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// ── Cells ──────────────────────────────────────────────────────────────────

function ValueCell({ value, winner }: { value: string; winner: boolean }) {
  return (
    <span className={winner ? 'inline-flex items-center gap-1.5 font-semibold text-green-700' : 'text-gray-700'}>
      {value}
      {winner && <span aria-label="Winner" className="text-xs">●</span>}
    </span>
  )
}

function ChipList({ items }: { items: string[] }) {
  if (!items.length) return <span className="text-gray-400">—</span>
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((s) => (
        <span key={s} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full capitalize">{s}</span>
      ))}
    </div>
  )
}

// ── Utilities ──────────────────────────────────────────────────────────────

function range(min: number | null, max: number | null, suffix: string): string {
  if (min != null && max != null) return `${min}–${max}${suffix}`
  if (max != null) return `up to ${max}${suffix}`
  return '—'
}

function winner(a: number | null, b: number | null): 'a' | 'b' | null {
  if (a == null || b == null) return null
  if (a > b) return 'a'
  if (b > a) return 'b'
  return null
}

function buildStrainSchema(s: Strain) {
  const props: Record<string, string>[] = []
  if (s.thc_min != null && s.thc_max != null) props.push({ name: 'THC', value: `${s.thc_min}-${s.thc_max}%` })
  if (s.cbd_min != null && s.cbd_max != null) props.push({ name: 'CBD', value: `${s.cbd_min}-${s.cbd_max}%` })
  if (s.flowering_time_days)                  props.push({ name: 'Flowering Time', value: `${s.flowering_time_days} days` })
  if (s.difficulty)                           props.push({ name: 'Difficulty', value: s.difficulty })

  return {
    '@context': 'https://schema.org',
    '@type': 'Thing',
    additionalType: 'CannabisStrainProfile',
    name: s.name,
    description: s.short_description ?? s.description ?? `${s.name} cannabis strain profile`,
    url: `${baseUrl}/strains/${s.slug}`,
    additionalProperty: props.map((p) => ({ '@type': 'PropertyValue', ...p })),
  }
}
