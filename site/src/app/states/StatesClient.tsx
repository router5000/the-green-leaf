'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import type React from 'react'
import type { StateData } from '@/data/statesData'

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

const STATUS_LABEL: Record<StateData['legalStatus'], string> = {
  recreational: 'Recreational',
  medical: 'Medical Only',
  illegal: 'Illegal',
}

const STATUS_BADGE: Record<StateData['legalStatus'], string> = {
  recreational: 'bg-leaf-100 text-leaf-700',
  medical: 'bg-amber-100 text-amber-700',
  illegal: 'bg-red-100 text-red-600',
}

type Filter = 'all' | StateData['legalStatus']

const FILTERS: { label: string; value: Filter }[] = [
  { label: 'All States', value: 'all' },
  { label: 'Recreational', value: 'recreational' },
  { label: 'Medical Only', value: 'medical' },
  { label: 'Illegal', value: 'illegal' },
]

export default function StatesClient({ states }: { states: StateData[] }) {
  const [filter, setFilter] = useState<Filter>('all')

  const filtered = useMemo(
    () => filter === 'all' ? states : states.filter(s => s.legalStatus === filter),
    [states, filter]
  )

  const counts = useMemo(() => ({
    all: states.length,
    recreational: states.filter(s => s.legalStatus === 'recreational').length,
    medical: states.filter(s => s.legalStatus === 'medical').length,
    illegal: states.filter(s => s.legalStatus === 'illegal').length,
  }), [states])

  return (
    <div className="bg-[#f0f0f0]">
      {/* ── Separator — below nav bar ───────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Hero ───────────────────────────────────────────────────── */}
      <div className="relative py-16 overflow-hidden">
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
        <div className="relative z-10 max-w-6xl mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#1a3a0a' }}>
            Cannabis Laws by State
          </h1>
          <p className="text-xl max-w-2xl" style={{ color: '#2d4a1e' }}>
            Current possession limits, home-grow rules, and legal status for all 50 US states.
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <span
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium"
              style={{ backgroundColor: 'rgba(26,58,10,0.08)', color: '#1a3a0a' }}
            >
              {counts.recreational} recreational
            </span>
            <span
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium"
              style={{ backgroundColor: 'rgba(180,120,0,0.10)', color: '#7a5200' }}
            >
              {counts.medical} medical only
            </span>
            <span
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium"
              style={{ backgroundColor: 'rgba(180,30,30,0.08)', color: '#8a1a1a' }}
            >
              {counts.illegal} illegal
            </span>
          </div>
        </div>
      </div>

      {/* ── Separator ──────────────────────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── States grid — dot-panel layout ─────────────────────────── */}
      <section className="relative bg-[#f0f0f0] overflow-hidden">
        <div className="relative grid md:grid-cols-[160px_1fr_160px]">
          {/* Left dot panel */}
          <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

          {/* Center content */}
          <div className="min-w-0 py-12">
            <div className="max-w-6xl mx-auto px-4">

              {/* Filter buttons */}
              <div className="flex flex-wrap gap-2 mb-8">
                {FILTERS.map(btn => (
                  <button
                    key={btn.value}
                    onClick={() => setFilter(btn.value)}
                    className={`px-5 py-2 rounded-full text-sm font-medium transition-colors ${
                      filter === btn.value
                        ? 'bg-[#1a3a0a] text-white'
                        : 'bg-transparent border border-[#1a3a0a] text-[#1a3a0a] hover:bg-[#1a3a0a]/10'
                    }`}
                  >
                    {btn.label}
                    <span className={`ml-1.5 text-xs ${filter === btn.value ? 'opacity-70' : 'opacity-50'}`}>
                      {counts[btn.value]}
                    </span>
                  </button>
                ))}
              </div>

              {/* State cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {filtered.map(state => (
                  <Link
                    key={state.slug}
                    href={`/states/${state.slug}`}
                    className="no-underline block group"
                  >
                    <article className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300 h-full flex flex-col">
                      {/* Hero image */}
                      <div className="relative h-24 flex-shrink-0 overflow-hidden">
                        <Image
                          src={`/images/states/${state.slug}-hero.jpg`}
                          alt={`${state.name} cannabis laws`}
                          fill
                          className="object-cover grayscale group-hover:grayscale-0 group-hover:scale-105 transition-all duration-500"
                          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
                        />
                        <span
                          className={`absolute top-2 right-2 z-10 px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[state.legalStatus]}`}
                        >
                          {STATUS_LABEL[state.legalStatus]}
                        </span>
                      </div>

                      {/* Content */}
                      <div className="p-4 flex flex-col flex-1">
                        <h2 className="text-sm font-semibold text-neutral-900 mb-2 group-hover:text-leaf-700 transition-colors">
                          {state.name}
                        </h2>
                        <p className="text-xs text-neutral-500 line-clamp-2 flex-1 mb-3">
                          {state.possessionLimit}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-neutral-400">Age {state.purchaseAge}+</span>
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
