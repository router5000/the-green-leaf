'use client'

import Globe from '@/components/ui/Globe'
import MagicTransform from '@/components/ui/MagicTransform'

function DashedLine() {
  return (
    <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
    </svg>
  )
}

function CornerSquare({ style, className = '' }: { style: React.CSSProperties; className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={className}
      style={{
        position: 'absolute',
        width: '12px',
        height: '12px',
        border: '1px solid #d4d4d4',
        backgroundColor: '#f0f0f0',
        zIndex: 2,
        ...style,
      }}
    />
  )
}

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

export default function GlobeSection() {
  return (
    <section className="relative bg-[#f0f0f0] overflow-hidden">

      {/* Top separator */}
      <DashedLine />

      {/* ── Globe + feature grid ─────────────────────────────────── */}
      <div className="relative grid md:grid-cols-[160px_1fr_160px]">
        <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

        <div className="min-w-0">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center pt-16 pb-8">
            <h2 className="font-serif font-bold text-gray-900 leading-tight mb-4" style={{ fontSize: 'clamp(1.9rem, 4vw, 3rem)' }}>
              Your Cannabis Resource
            </h2>
            <p className="text-gray-500 text-lg leading-relaxed">
              Comprehensive guides for growers, enthusiasts, and wellness seekers
            </p>
          </div>

          <div className="w-full">
            <Globe
              primaryColor="rgb(45, 106, 15)" neutralColor="rgba(45, 106, 15, 0.5)"
              atmosphereColor="rgba(45, 106, 15, 0.08)" atmosphereAltitude={0.15}
              showAtmosphere globeColor="rgba(0,0,0,0)" globeOpacity={0}
              pointSize={0.3} autoRotateSpeed={0.85} arcCount={10}
              landDotRows={200} width="auto" height={600}
            />
          </div>

          <div className="relative z-10 bg-[#f0f0f0]" style={{ marginTop: '-120px' }}>
            <div className="relative" style={{ border: '1px solid #d4d4d4', overflow: 'visible' }}>
              <CornerSquare style={{ top: '-6px',    left: '-6px'  }} />
              <CornerSquare style={{ top: '-6px',    right: '-6px' }} />
              <CornerSquare style={{ bottom: '-6px', left: '-6px'  }} />
              <CornerSquare style={{ bottom: '-6px', right: '-6px' }} />

              <div className="relative" style={{ borderBottom: '1px solid #d4d4d4', overflow: 'visible' }}>
                <CornerSquare className="hidden md:block" style={{ bottom: '-6px', left: '-6px' }} />
                <CornerSquare className="hidden md:block" style={{ bottom: '-6px', right: '-6px' }} />
                <div className="grid md:grid-cols-3">
                  <div className="py-8 md:py-10 px-8 md:px-10 border-b border-[#d4d4d4] md:border-b-0 md:border-r">
                    <div className="w-9 h-9 rounded-lg bg-[#f0f7ed] flex items-center justify-center mb-5">
                      <svg className="w-5 h-5 text-[#2D5016]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" /></svg>
                    </div>
                    <h3 className="font-semibold text-gray-900 text-lg mb-2">Strain Guides</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">Explore indica, sativa &amp; hybrids with detailed terpene and effect profiles</p>
                  </div>
                  <div className="py-8 md:py-10 px-8 md:px-10 border-b border-[#d4d4d4] md:border-b-0 md:border-r">
                    <div className="w-9 h-9 rounded-lg bg-[#f0f7ed] flex items-center justify-center mb-5">
                      <svg className="w-5 h-5 text-[#2D5016]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" /></svg>
                    </div>
                    <h3 className="font-semibold text-gray-900 text-lg mb-2">Growing Tips</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">Indoor, outdoor &amp; hydroponic techniques for every skill level</p>
                  </div>
                  <div className="py-8 md:py-10 px-8 md:px-10">
                    <div className="w-9 h-9 rounded-lg bg-[#f0f7ed] flex items-center justify-center mb-5">
                      <svg className="w-5 h-5 text-[#2D5016]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" /></svg>
                    </div>
                    <h3 className="font-semibold text-gray-900 text-lg mb-2">Wellness Insights</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">CBD, medical cannabis &amp; health application guides</p>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-3">
                <div className="py-8 md:py-10 px-8 md:px-10 border-b border-[#d4d4d4] md:border-b-0 md:border-r">
                  <div className="w-9 h-9 rounded-lg bg-[#f0f7ed] flex items-center justify-center mb-5">
                    <svg className="w-5 h-5 text-[#2D5016]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" /></svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg mb-2">Consumption Methods</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">Learn about smoking, edibles, vaping, tinctures, and topicals</p>
                </div>
                <div className="py-8 md:py-10 px-8 md:px-10 border-b border-[#d4d4d4] md:border-b-0 md:border-r">
                  <div className="w-9 h-9 rounded-lg bg-[#f0f7ed] flex items-center justify-center mb-5">
                    <svg className="w-5 h-5 text-[#2D5016]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5M6 7.5h3v3H6v-3z" /></svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg mb-2">Legal &amp; Industry</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">Stay informed on legalization, state laws, and industry developments</p>
                </div>
                <div className="py-8 md:py-10 px-8 md:px-10">
                  <div className="w-9 h-9 rounded-lg bg-[#f0f7ed] flex items-center justify-center mb-5">
                    <svg className="w-5 h-5 text-[#2D5016]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" /></svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg mb-2">Culture &amp; Lifestyle</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">Explore cannabis culture, recipes, history, and lifestyle content</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />
        <VerticalDash side="left" />
        <VerticalDash side="right" />
      </div>

      {/* ── MagicTransform section ───────────────────────────────── */}
      <div className="relative grid md:grid-cols-[160px_1fr_160px]">
        <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

        <div className="min-w-0 px-4 sm:px-8 py-16 sm:py-20">
          <div className="text-center mb-10">
            <h2 className="font-serif font-bold text-gray-900 leading-tight mb-4" style={{ fontSize: 'clamp(1.6rem, 3.5vw, 2.5rem)' }}>
              Turning raw knowledge into cannabis clarity
            </h2>
            <p className="text-gray-500 text-lg leading-relaxed max-w-xl mx-auto">
              Our content pipeline transforms complex cannabis science into guides you can actually use
            </p>
          </div>

          <MagicTransform
            width="100%" height={500} axisColor="#2d6a0f"
            backgroundColor="transparent" documentDuration={4} particleCount={18}
            results={[
              { id: "strain",   label: "strain guide", color: "#2d6a0f", textColor: "#ffffff" },
              { id: "grow",     label: "grow tip",      color: "#1a3a0a", textColor: "#ffffff" },
              { id: "wellness", label: "wellness",      color: "#4a8c2a", textColor: "#ffffff" },
              { id: "legal",    label: "legal update",  color: "#0d2406", textColor: "#ffffff" },
              { id: "culture",  label: "culture",       color: "#6aad3a", textColor: "#ffffff" },
            ]}
          />
        </div>

        <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />
        <VerticalDash side="left" />
        <VerticalDash side="right" />
      </div>

      {/* Bottom separator */}
      <DashedLine />

    </section>
  )
}
