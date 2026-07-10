import fs from 'fs'
import path from 'path'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { statesData, getStateBySlug } from '@/data/statesData'
import type { StateData } from '@/data/statesData'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import type { Metadata } from 'next'
import type React from 'react'

const baseUrl = 'https://strainreport.com'

// ── Shared layout helpers ──────────────────────────────────────────────────

function VerticalDash({ side }: { side: 'left' | 'right' }) {
  return (
    <div
      className={`absolute ${side}-[160px] top-0 bottom-0 hidden md:block pointer-events-none`}
      aria-hidden="true"
    >
      <svg width="1" height="100%" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <line x1="0.5" y1="0" x2="0.5" y2="100%" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>
    </div>
  )
}

const dotGridStyle: React.CSSProperties = {
  backgroundImage: 'radial-gradient(circle, #c8c8c8 1px, transparent 1px)',
  backgroundSize: '20px 20px',
  backgroundColor: '#f0f0f0',
}

// ── Status helpers ─────────────────────────────────────────────────────────

const STATUS_LABEL: Record<StateData['legalStatus'], string> = {
  recreational: 'Recreational',
  medical: 'Medical Only',
  illegal: 'Illegal',
}

const STATUS_BADGE_LIGHT: Record<StateData['legalStatus'], string> = {
  recreational: 'bg-leaf-100 text-leaf-700',
  medical: 'bg-amber-100 text-amber-700',
  illegal: 'bg-red-100 text-red-600',
}

const STATUS_BADGE_DARK: Record<StateData['legalStatus'], string> = {
  recreational: 'bg-green-600 text-white',
  medical: 'bg-amber-500 text-white',
  illegal: 'bg-red-600 text-white',
}

const STATUS_DOT: Record<StateData['legalStatus'], string> = {
  recreational: 'bg-leaf-500',
  medical: 'bg-amber-500',
  illegal: 'bg-red-500',
}

const STATUS_BORDER: Record<StateData['legalStatus'], string> = {
  recreational: 'border-leaf-400',
  medical: 'border-amber-400',
  illegal: 'border-red-400',
}

// ── Static generation ──────────────────────────────────────────────────────

export function generateStaticParams() {
  return statesData.map(s => ({ slug: s.slug }))
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const state = getStateBySlug(slug)
  if (!state) return {}
  const statusPhrase =
    state.legalStatus === 'recreational'
      ? 'Adult-use recreational cannabis is legal'
      : state.legalStatus === 'medical'
      ? 'Medical cannabis program available'
      : 'Cannabis remains illegal'
  return {
    title: `${state.name} Cannabis Laws 2025 — Possession Limits & Regulations | The Strain Report`,
    description: `${statusPhrase} in ${state.name}. Possession limit: ${state.possessionLimit}. ${state.consumptionNote}`,
    alternates: { canonical: `${baseUrl}/states/${slug}` },
    openGraph: {
      title: `${state.name} Cannabis Laws 2025 | The Strain Report`,
      description: `Possession limits, home-grow rules, and dispensary info for ${state.name}.`,
      url: `${baseUrl}/states/${slug}`,
    },
  }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function StateDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const state = getStateBySlug(slug)
  if (!state) notFound()

  const heroPath = path.join(process.cwd(), 'public', 'images', 'states', `${slug}-hero.jpg`)
  const hasHeroImage = fs.existsSync(heroPath)

  // Pick 3 "more states" spread across the list
  const idx = statesData.findIndex(s => s.slug === slug)
  const moreStates = [
    statesData[(idx + 1) % statesData.length],
    statesData[(idx + 17) % statesData.length],
    statesData[(idx + 34) % statesData.length],
  ]

  return (
    <div className="bg-[#f0f0f0]">
      {/* ── Separator — below nav ─────────────────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Breadcrumb ────────────────────────────────────────────────────── */}
      <div className="max-w-6xl mx-auto px-4 py-3">
        <nav className="flex items-center gap-1.5 text-sm text-neutral-400" aria-label="Breadcrumb">
          <Link href="/" className="hover:text-leaf-700 transition-colors">Home</Link>
          <span>/</span>
          <Link href="/states" className="hover:text-leaf-700 transition-colors">States</Link>
          <span>/</span>
          <span className="text-neutral-700 font-medium">{state.name}</span>
        </nav>
      </div>

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <div className="relative w-full h-64 md:h-80 overflow-hidden">
        {hasHeroImage ? (
          <>
            <Image
              src={`/images/states/${slug}-hero.jpg`}
              alt={`${state.name} cannabis laws`}
              fill
              className="object-cover"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/20 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 pb-8">
              <div className="max-w-6xl mx-auto px-4">
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">{state.name}</h1>
                <span className={`px-4 py-1.5 rounded-full text-sm font-semibold ${STATUS_BADGE_DARK[state.legalStatus]}`}>
                  {STATUS_LABEL[state.legalStatus]}
                </span>
              </div>
            </div>
          </>
        ) : (
          <>
            <BlinkingSquares
              className="absolute inset-0"
              width="100%"
              height="100%"
              direction="right"
              gridSize={52}
              squareColor="#1a5276"
              backgroundColor="#f0f0f0"
              falloff={1.25}
              fadeStart={0.33}
              fadeEnd={1}
              squareSize={0.57}
              minBrightness={0.55}
              twinkleSpeed={1.4}
              twinkleStrength={0.94}
              intensity={1}
              opacity={0.4}
              dpr={1.5}
            />
            <div className="absolute bottom-0 left-0 right-0 pb-8">
              <div className="max-w-6xl mx-auto px-4">
                <h1 className="text-4xl md:text-5xl font-bold mb-3" style={{ color: '#1a3a0a' }}>
                  {state.name}
                </h1>
                <span className={`px-4 py-1.5 rounded-full text-sm font-semibold ${STATUS_BADGE_LIGHT[state.legalStatus]}`}>
                  {STATUS_LABEL[state.legalStatus]}
                </span>
              </div>
            </div>
          </>
        )}
      </div>

      {/* ── Separator ────────────────────────────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Content — dot-panel layout ───────────────────────────────────── */}
      <section className="relative bg-[#f0f0f0] overflow-hidden">
        <div className="relative grid md:grid-cols-[160px_1fr_160px]">
          {/* Left dot panel */}
          <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

          {/* Center content */}
          <div className="min-w-0 py-12">
            <div className="max-w-6xl mx-auto px-4 space-y-6">

              {/* ── Quick Facts strip ──────────────────────────────────── */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <div className="text-[10px] text-neutral-400 uppercase tracking-widest mb-2">Legal Status</div>
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full flex-shrink-0 ${STATUS_DOT[state.legalStatus]}`} />
                    <span className="text-sm font-semibold text-neutral-800 leading-tight">
                      {STATUS_LABEL[state.legalStatus]}
                    </span>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-4 shadow-sm sm:col-span-2">
                  <div className="text-[10px] text-neutral-400 uppercase tracking-widest mb-2">Possession Limit</div>
                  <div className="text-sm font-semibold text-neutral-800 leading-snug line-clamp-2">
                    {state.possessionLimit}
                  </div>
                </div>

                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <div className="text-[10px] text-neutral-400 uppercase tracking-widest mb-2">Minimum Age</div>
                  <div className="text-sm font-semibold text-neutral-800">{state.purchaseAge}+</div>
                </div>

                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <div className="text-[10px] text-neutral-400 uppercase tracking-widest mb-2">Dispensaries</div>
                  <div className={`text-sm font-semibold ${state.dispensaries ? 'text-leaf-700' : 'text-red-600'}`}>
                    {state.dispensaries ? 'Open' : 'None'}
                  </div>
                </div>
              </div>

              {/* ── What's Legal ──────────────────────────────────────── */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-xl font-bold text-neutral-900 mb-3">What&apos;s Legal</h2>
                <p className="text-neutral-600 leading-relaxed">{state.consumptionNote}</p>
              </div>

              {/* ── Possession Limits ─────────────────────────────────── */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-xl font-bold text-neutral-900 mb-3">Possession Limits</h2>
                <p className="text-neutral-600 leading-relaxed">{state.possessionLimit}</p>
              </div>

              {/* ── Home Growing ──────────────────────────────────────── */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-xl font-bold text-neutral-900 mb-3">Home Growing</h2>
                <p className="text-neutral-600 leading-relaxed">{state.homeGrow}</p>
              </div>

              {/* ── Penalties ─────────────────────────────────────────── */}
              <div className={`bg-white rounded-xl p-6 shadow-sm border-l-4 ${STATUS_BORDER[state.legalStatus]}`}>
                <h2 className="text-xl font-bold text-neutral-900 mb-3">Penalties</h2>
                {state.penalties ? (
                  <p className="text-neutral-600 leading-relaxed">{state.penalties}</p>
                ) : (
                  <p className="text-neutral-600 leading-relaxed">
                    Adult-use cannabis is legal in {state.name}. Consuming in prohibited public spaces
                    or exceeding possession limits may still result in a civil fine.
                  </p>
                )}
              </div>

              {/* ── Official Resource ─────────────────────────────────── */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-xl font-bold text-neutral-900 mb-2">Official Resource</h2>
                <p className="text-neutral-500 text-sm mb-4">
                  For the most up-to-date rules and licensing information, visit the official state agency.
                </p>
                <a
                  href={state.officialLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium bg-[#1a3a0a] text-white hover:bg-[#2d5016] transition-colors"
                >
                  Visit Official Site →
                </a>
              </div>

              {/* ── More States ───────────────────────────────────────── */}
              <div className="pt-4">
                <h2 className="text-2xl font-bold text-neutral-900 mb-6">More States</h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {moreStates.map(s => (
                    <Link
                      key={s.slug}
                      href={`/states/${s.slug}`}
                      className="no-underline block group"
                    >
                      <article className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300 h-full flex flex-col">
                        <div className="relative h-24 flex-shrink-0 overflow-hidden">
                          <div className="absolute inset-0 bg-gray-200 grayscale group-hover:grayscale-0 group-hover:scale-105 transition-all duration-500" />
                          <span className={`absolute top-2 right-2 z-10 px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE_LIGHT[s.legalStatus]}`}>
                            {STATUS_LABEL[s.legalStatus]}
                          </span>
                        </div>
                        <div className="p-4 flex flex-col flex-1">
                          <h3 className="text-sm font-semibold text-neutral-900 mb-2 group-hover:text-leaf-700 transition-colors">
                            {s.name}
                          </h3>
                          <p className="text-xs text-neutral-500 line-clamp-2 flex-1 mb-3">
                            {s.possessionLimit}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-neutral-400">Age {s.purchaseAge}+</span>
                            <span className="text-xs font-medium text-leaf-600 group-hover:text-leaf-800 transition-colors">
                              View Guide →
                            </span>
                          </div>
                        </div>
                      </article>
                    </Link>
                  ))}
                </div>
              </div>

            </div>
          </div>

          {/* Right dot panel */}
          <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

          <VerticalDash side="left" />
          <VerticalDash side="right" />
        </div>
      </section>

      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>
    </div>
  )
}
