import { getSupabase } from '@/lib/supabase'
import Link from 'next/link'
import BlinkingSquares from '@/components/ui/BlinkingSquares'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'

const baseUrl = 'https://strainreport.com'

export const metadata: Metadata = {
  title: 'Strain Database - Cannabis Strains | The Strain Report',
  description: 'Browse our comprehensive cannabis strain database. Find detailed profiles on effects, terpenes, THC/CBD levels, and growing tips for hundreds of strains.',
  openGraph: {
    title: 'Strain Database | The Strain Report',
    description: 'Browse our comprehensive cannabis strain database. Find detailed profiles on effects, terpenes, THC/CBD levels, and growing tips.',
    url: `${baseUrl}/strains`,
    siteName: 'The Strain Report',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Strain Database | The Strain Report',
    description: 'Browse our comprehensive cannabis strain database.',
  },
  alternates: { canonical: `${baseUrl}/strains` },
}

type Strain = {
  id: string
  name: string
  slug: string
  strain_type: 'indica' | 'sativa' | 'hybrid'
  thc_min: number | null
  thc_max: number | null
  short_description: string | null
  flavors: string[] | null
}

const TYPE_BADGE: Record<string, string> = {
  indica: 'bg-purple-100 text-purple-700',
  sativa: 'bg-green-100 text-green-700',
  hybrid: 'bg-orange-100 text-orange-600',
}

export default async function StrainsPage() {
  let strains: Strain[] = []
  try {
    const { data } = await getSupabase()
      .from('strains')
      .select('id, name, slug, strain_type, thc_min, thc_max, short_description, flavors')
      .eq('published', true)
      .order('name')
    strains = data ?? []
  } catch {
    // env vars unavailable during static build — render empty list
  }

  return (
    <div className="bg-[#f0f0f0]">
      {/* ── Separator — below nav bar ────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Hero ───────────────────────────────────────────── */}
      <div className="relative py-16 overflow-hidden">
        <BlinkingSquares
          className="absolute inset-0"
          width="100%"
          height="100%"
          direction="right"
          gridSize={52}
          squareColor="#F59E0B"
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
            Cannabis Strain Database
          </h1>
          <p className="text-xl max-w-2xl mb-4" style={{ color: '#2d4a1e' }}>
            Detailed profiles on effects, terpenes, genetics, and growing info for 200+ strains.
          </p>
          <span
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/70 backdrop-blur-sm text-sm font-medium border border-amber-300/40"
            style={{ color: '#2d4a1e' }}
          >
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            {strains.length} {strains.length === 1 ? 'strain' : 'strains'} in the database
          </span>
        </div>
      </div>

      {/* ── Separator ─────────────────────────────────────── */}
      <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
      </svg>

      {/* ── Grid ──────────────────────────────────────────── */}
      <div className="px-4 sm:px-6 md:px-[160px] py-12">
        {strains.length === 0 ? (
          <p className="text-gray-400 text-center py-16">No strains found.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {strains.map((strain) => (
              <StrainCard key={strain.id} strain={strain} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StrainCard({ strain }: { strain: Strain }) {
  const topFlavors = strain.flavors?.slice(0, 2) ?? []
  const thcRange =
    strain.thc_min != null && strain.thc_max != null
      ? `THC ${strain.thc_min}–${strain.thc_max}%`
      : strain.thc_max != null
        ? `THC up to ${strain.thc_max}%`
        : null

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 flex flex-col gap-3 hover:border-[#2D5016]/30 hover:shadow-sm transition-all">
      <div className="flex items-start justify-between gap-2">
        <h2 className="font-serif text-xl text-gray-900 leading-tight">{strain.name}</h2>
        <span
          className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full capitalize ${
            TYPE_BADGE[strain.strain_type] ?? 'bg-gray-100 text-gray-600'
          }`}
        >
          {strain.strain_type}
        </span>
      </div>

      {thcRange && (
        <p className="text-sm text-gray-500 font-medium">{thcRange}</p>
      )}

      {strain.short_description && (
        <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">{strain.short_description}</p>
      )}

      {topFlavors.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {topFlavors.map((f) => (
            <span key={f} className="text-xs bg-gray-100 text-gray-500 px-2.5 py-1 rounded-full capitalize">
              {f}
            </span>
          ))}
        </div>
      )}

      <Link
        href={`/strains/${strain.slug}`}
        className="mt-auto pt-2 text-sm font-medium text-[#2D5016] hover:text-[#3a6b1e] no-underline inline-flex items-center gap-1 transition-colors"
      >
        View Strain <span aria-hidden="true">→</span>
      </Link>
    </div>
  )
}
