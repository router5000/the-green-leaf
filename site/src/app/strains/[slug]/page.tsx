import { getSupabase } from '@/lib/supabase'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import type { Metadata } from 'next'

const baseUrl = 'https://strainreport.com'

const TYPE_BADGE: Record<string, string> = {
  indica: 'bg-purple-100 text-purple-700',
  sativa: 'bg-green-100 text-green-700',
  hybrid: 'bg-orange-100 text-orange-600',
}

const EFFECT_TYPE_LABEL: Record<string, string> = {
  positive: 'Positive Effects',
  medical:  'Medical Benefits',
  negative: 'Side Effects',
}

const EFFECT_TYPE_STYLE: Record<string, string> = {
  positive: 'bg-green-50 text-green-700 border-green-200',
  medical:  'bg-blue-50 text-blue-700 border-blue-200',
  negative: 'bg-red-50 text-red-600 border-red-200',
}

const DIFFICULTY_BADGE: Record<string, string> = {
  easy:       'bg-green-100 text-green-700',
  moderate:   'bg-amber-100 text-amber-700',
  difficult:  'bg-red-100 text-red-600',
}

// ── Types ──────────────────────────────────────────────────────────────────

type StrainSeo = { meta_title: string | null; meta_description: string | null }
type Effect    = { id: string; effect_name: string; effect_type: string; intensity: number | null }
type Terpene   = { id: string; terpene_name: string; percentage: number | null }
type Genetic   = { id: string; parent_strain_name: string; parent_type: string }

type Strain = {
  id: string
  name: string
  slug: string
  aka: string[] | null
  strain_type: string
  thc_min: number | null
  thc_max: number | null
  cbd_min: number | null
  cbd_max: number | null
  description: string | null
  short_description: string | null
  flavors: string[] | null
  aromas: string[] | null
  colors: string[] | null
  difficulty: string | null
  flowering_time_days: number | null
  yield_indoor: string | null
  yield_outdoor: string | null
  height_indoor: string | null
  height_outdoor: string | null
  origin_country: string | null
  strain_seo: StrainSeo[]
  effects: Effect[]
  terpenes: Terpene[]
  genetics: Genetic[]
}

// ── Metadata ───────────────────────────────────────────────────────────────

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  let data: { name: string; strain_seo: StrainSeo[] } | null = null
  try {
    const result = await getSupabase()
      .from('strains')
      .select('name, strain_seo(meta_title, meta_description)')
      .eq('slug', slug)
      .single()
    data = result.data as unknown as { name: string; strain_seo: StrainSeo[] }
  } catch {
    // env vars unavailable during static build
  }

  if (!data) return {}

  const seo = data.strain_seo?.[0]
  const title = seo?.meta_title ?? `${data.name} Strain | The Strain Report`
  const description = seo?.meta_description ?? undefined

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `${baseUrl}/strains/${slug}`,
      siteName: 'The Strain Report',
      type: 'website',
    },
    twitter: { card: 'summary_large_image', title, description },
    alternates: { canonical: `${baseUrl}/strains/${slug}` },
  }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function StrainDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params

  let strain: unknown = null
  try {
    const result = await getSupabase()
      .from('strains')
      .select(`
        *,
        strain_seo(*),
        effects(*),
        terpenes(*),
        genetics(*)
      `)
      .eq('slug', slug)
      .eq('published', true)
      .single()
    strain = result.data
  } catch {
    // env vars unavailable during static build
  }

  if (!strain) notFound()

  const s = strain as unknown as Strain
  const effectsByType = (s.effects ?? []).reduce<Record<string, Effect[]>>((acc, e) => {
    ;(acc[e.effect_type] ??= []).push(e)
    return acc
  }, {})
  const maxTerpene = Math.max(...(s.terpenes ?? []).map((t) => t.percentage ?? 0), 0.01)

  return (
    <div className="min-h-screen bg-[#f0f0f0]">
      <div className="px-4 sm:px-6 md:px-[160px] pt-10 pb-16">

        {/* Back link */}
        <Link
          href="/strains"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-[#2D5016] no-underline mb-8 transition-colors"
        >
          ← Strain Database
        </Link>

        {/* Hero */}
        <div className="flex flex-wrap items-start gap-3 mb-2">
          <h1 className="font-serif text-4xl md:text-5xl text-gray-900">{s.name}</h1>
          <span className={`mt-2 text-sm font-medium px-3 py-1 rounded-full capitalize ${TYPE_BADGE[s.strain_type] ?? 'bg-gray-100 text-gray-600'}`}>
            {s.strain_type}
          </span>
        </div>

        {s.aka && s.aka.length > 0 && (
          <p className="text-sm text-gray-400 mb-4">Also known as: {s.aka.join(', ')}</p>
        )}

        {/* THC / CBD pills */}
        <div className="flex flex-wrap gap-3 mb-6">
          {s.thc_min != null && s.thc_max != null && (
            <StatPill label="THC" value={`${s.thc_min}–${s.thc_max}%`} />
          )}
          {s.cbd_min != null && s.cbd_max != null && (
            <StatPill label="CBD" value={`${s.cbd_min}–${s.cbd_max}%`} />
          )}
          {s.origin_country && (
            <StatPill label="Origin" value={s.origin_country} />
          )}
        </div>

        {s.short_description && (
          <p className="text-lg text-gray-600 leading-relaxed mb-10 max-w-3xl">{s.short_description}</p>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main column */}
          <div className="lg:col-span-2 flex flex-col gap-8">

            {/* Overview */}
            {s.description && (
              <Section title="Overview">
                <p className="text-gray-600 leading-relaxed whitespace-pre-line">{s.description}</p>
              </Section>
            )}

            {/* Effects */}
            {s.effects && s.effects.length > 0 && (
              <Section title="Effects">
                <div className="flex flex-col gap-5">
                  {(['positive', 'medical', 'negative'] as const).map((type) => {
                    const group = effectsByType[type]
                    if (!group?.length) return null
                    return (
                      <div key={type}>
                        <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                          {EFFECT_TYPE_LABEL[type]}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {group.map((e) => (
                            <span
                              key={e.id}
                              className={`text-sm px-3 py-1.5 rounded-full border capitalize font-medium ${EFFECT_TYPE_STYLE[type]}`}
                            >
                              {e.effect_name}
                              {e.intensity != null && (
                                <span className="ml-1.5 opacity-60 text-xs">{'●'.repeat(e.intensity)}{'○'.repeat(5 - e.intensity)}</span>
                              )}
                            </span>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </Section>
            )}

            {/* Terpenes */}
            {s.terpenes && s.terpenes.length > 0 && (
              <Section title="Terpenes">
                <div className="flex flex-col gap-3">
                  {s.terpenes.map((t) => (
                    <div key={t.id}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-700 capitalize font-medium">{t.terpene_name}</span>
                        {t.percentage != null && (
                          <span className="text-gray-400">{t.percentage.toFixed(2)}%</span>
                        )}
                      </div>
                      {t.percentage != null && (
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[#2D5016] rounded-full"
                            style={{ width: `${Math.min((t.percentage / maxTerpene) * 100, 100)}%` }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Genetics */}
            {s.genetics && s.genetics.length > 0 && (
              <Section title="Genetics">
                <div className="flex flex-wrap gap-3">
                  {s.genetics.map((g) => (
                    <div key={g.id} className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-sm">
                      <p className="text-xs text-gray-400 capitalize mb-0.5">{g.parent_type}</p>
                      <p className="text-gray-800 font-medium">{g.parent_strain_name}</p>
                    </div>
                  ))}
                </div>
              </Section>
            )}
          </div>

          {/* Sidebar — Growing Info */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 p-6 sticky top-20">
              <h2 className="font-serif text-xl text-gray-900 mb-5">Growing Info</h2>
              <div className="flex flex-col gap-4">
                {s.difficulty && (
                  <GrowStat label="Difficulty">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${DIFFICULTY_BADGE[s.difficulty] ?? 'bg-gray-100 text-gray-600'}`}>
                      {s.difficulty}
                    </span>
                  </GrowStat>
                )}
                {s.flowering_time_days && (
                  <GrowStat label="Flowering Time" value={`${s.flowering_time_days} days`} />
                )}
                {s.yield_indoor && (
                  <GrowStat label="Yield (Indoor)" value={s.yield_indoor} />
                )}
                {s.yield_outdoor && (
                  <GrowStat label="Yield (Outdoor)" value={s.yield_outdoor} />
                )}
                {s.height_indoor && (
                  <GrowStat label="Height (Indoor)" value={s.height_indoor} />
                )}
                {s.height_outdoor && (
                  <GrowStat label="Height (Outdoor)" value={s.height_outdoor} />
                )}
                {s.flavors && s.flavors.length > 0 && (
                  <GrowStat label="Flavors">
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {s.flavors.map((f) => (
                        <span key={f} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full capitalize">{f}</span>
                      ))}
                    </div>
                  </GrowStat>
                )}
                {s.aromas && s.aromas.length > 0 && (
                  <GrowStat label="Aromas">
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {s.aromas.map((a) => (
                        <span key={a} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full capitalize">{a}</span>
                      ))}
                    </div>
                  </GrowStat>
                )}
                {s.colors && s.colors.length > 0 && (
                  <GrowStat label="Colors">
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {s.colors.map((c) => (
                        <span key={c} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full capitalize">{c}</span>
                      ))}
                    </div>
                  </GrowStat>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Shared sub-components ──────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="font-serif text-xl text-gray-900 mb-4">{title}</h2>
      {children}
    </div>
  )
}

function StatPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-4 py-2 text-sm">
      <span className="text-gray-400 mr-1.5">{label}</span>
      <span className="font-semibold text-gray-800">{value}</span>
    </div>
  )
}

function GrowStat({ label, value, children }: { label: string; value?: string; children?: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
      {value && <p className="text-sm text-gray-700 font-medium">{value}</p>}
      {children}
    </div>
  )
}
