'use client'

function DashedLine() {
  return (
    <svg width="100%" height="1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <line x1="0" y1="0.5" x2="100%" y2="0.5" stroke="#d4d4d4" strokeWidth="1" strokeDasharray="16,16" />
    </svg>
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

const TICKER_ITEMS = [
  'Expert-written guides', 'Science-backed content', 'Strain database',
  'Growing techniques', 'Wellness insights', 'Legal updates',
  'Culture & lifestyle', 'Beginner friendly', 'Updated regularly', 'Free to access',
]

// All cards kept within the upper 75% of the card, inset from edges
const FLOAT_CARDS_LEFT = [
  { icon: 'sparkles', top: '10%', left: '7%',  anim: 'cta-float-a', dur: '6s',  delay: '0s'   },
  { icon: 'sun',      top: '35%', left: '16%', anim: 'cta-float-b', dur: '8s',  delay: '1.5s' },
  { icon: 'beaker',   top: '60%', left: '9%',  anim: 'cta-float-c', dur: '10s', delay: '3s'   },
]
const FLOAT_CARDS_RIGHT = [
  { icon: 'dropper',  top: '10%', right: '7%',  anim: 'cta-float-b', dur: '7s',  delay: '0.5s' },
  { icon: 'book',     top: '35%', right: '16%', anim: 'cta-float-a', dur: '9s',  delay: '2s'   },
  { icon: 'shield',   top: '60%', right: '9%',  anim: 'cta-float-c', dur: '11s', delay: '4s'   },
]

function FloatIcon({ icon }: { icon: string }) {
  if (icon === 'sparkles') return (
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="rgba(255,255,255,0.85)" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
    </svg>
  )
  if (icon === 'sun') return (
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="rgba(255,255,255,0.85)" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
    </svg>
  )
  if (icon === 'beaker') return (
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="rgba(255,255,255,0.85)" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
    </svg>
  )
  if (icon === 'dropper') return (
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="rgba(255,255,255,0.85)" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
    </svg>
  )
  if (icon === 'book') return (
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="rgba(255,255,255,0.85)" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
    </svg>
  )
  return (
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="rgba(255,255,255,0.85)" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  )
}

export default function CTASection() {
  return (
    <div className="relative bg-[#f0f0f0]">

      <DashedLine />

      <div className="relative grid md:grid-cols-[160px_1fr_160px]">

        {/* Left dot-grid panel */}
        <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

        {/* Center column */}
        <div className="min-w-0 relative px-4 sm:px-5 py-8 sm:py-10">

          {/* Corner squares at top boundary */}
          <div className="hidden md:block" aria-hidden="true" style={{ position: 'absolute', top: 0, left: 0, transform: 'translate(-50%, -50%)', width: 12, height: 12, border: '1px solid #d4d4d4', backgroundColor: '#f0f0f0', zIndex: 10 }} />
          <div className="hidden md:block" aria-hidden="true" style={{ position: 'absolute', top: 0, right: 0, transform: 'translate(50%, -50%)', width: 12, height: 12, border: '1px solid #d4d4d4', backgroundColor: '#f0f0f0', zIndex: 10 }} />

          {/* Keyframes */}
          <style>{`
            @keyframes cta-float-a{0%,100%{transform:translateY(0px) rotate(0deg)}50%{transform:translateY(-10px) rotate(1deg)}}
            @keyframes cta-float-b{0%,100%{transform:translateY(0px) rotate(0deg)}50%{transform:translateY(-14px) rotate(-1.5deg)}}
            @keyframes cta-float-c{0%,100%{transform:translateY(0px) rotate(0deg)}50%{transform:translateY(-8px) rotate(2deg)}}
            @keyframes cta-ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
          `}</style>

          {/* Dark green card */}
          <div className="relative rounded-2xl overflow-hidden" style={{ backgroundColor: '#1a3a0a', minHeight: 480 }}>

            {/* Dot texture */}
            <div className="absolute inset-0 pointer-events-none" aria-hidden="true" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '24px 24px' }} />

            {/* Bottom glow */}
            <div className="absolute bottom-0 left-0 right-0 h-3/5 pointer-events-none" aria-hidden="true" style={{ background: 'radial-gradient(ellipse 80% 100% at 50% 100%, rgba(74,140,42,0.15) 0%, transparent 70%)' }} />

            {/* Floating icon cards — left (upper 75%, inset from edges) */}
            {FLOAT_CARDS_LEFT.map((c) => (
              <div key={c.icon} className="absolute hidden sm:flex items-center justify-center" aria-hidden="true"
                style={{ left: c.left, top: c.top, width: 80, height: 80, border: '1px dashed rgba(255,255,255,0.3)', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 12, animation: `${c.anim} ${c.dur} ease-in-out infinite`, animationDelay: c.delay }}>
                <FloatIcon icon={c.icon} />
              </div>
            ))}

            {/* Floating icon cards — right (upper 75%, inset from edges) */}
            {FLOAT_CARDS_RIGHT.map((c) => (
              <div key={c.icon} className="absolute hidden sm:flex items-center justify-center" aria-hidden="true"
                style={{ right: c.right, top: c.top, width: 80, height: 80, border: '1px dashed rgba(255,255,255,0.3)', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 12, animation: `${c.anim} ${c.dur} ease-in-out infinite`, animationDelay: c.delay }}>
                <FloatIcon icon={c.icon} />
              </div>
            ))}

            {/* Center content */}
            <div className="relative z-10 flex flex-col items-center text-center px-8 sm:px-36 pt-16 pb-10">
              <h2 className="font-serif font-bold text-white leading-[1.06] tracking-tight mb-5" style={{ fontSize: 'clamp(2rem, 5vw, 3.75rem)' }}>
                Grow smarter,<br className="hidden sm:block" /> consume confidently
              </h2>
              <p className="text-base sm:text-lg leading-relaxed mb-10 max-w-lg" style={{ color: 'rgba(255,255,255,0.6)' }}>
                Join thousands of cannabis enthusiasts discovering strains, mastering cultivation, and understanding wellness — all in one place.
              </p>

              {/* CTA row: email capture */}
              <div className="flex flex-col items-center gap-1.5 w-full">
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full max-w-[300px] sm:max-w-none">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="rounded-full text-sm outline-none w-full sm:w-[220px]"
                    style={{ padding: '11px 20px', backgroundColor: '#ffffff', color: '#1a3a0a' }}
                  />
                  <button
                    type="button"
                    className="rounded-full font-semibold text-sm whitespace-nowrap transition-colors hover:bg-green-50 shrink-0 w-full sm:w-auto"
                    style={{ padding: '11px 20px', backgroundColor: '#ffffff', color: '#1a3a0a' }}
                  >
                    Get on the list
                  </button>
                </div>
                <p className="text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
                  Free cannabis education, no spam ever.
                </p>
              </div>
            </div>

            {/* Ticker bar */}
            <div className="overflow-hidden py-3" style={{ borderTop: '1px solid rgba(255,255,255,0.15)', backgroundColor: 'rgba(0,0,0,0.15)' }}>
              <div className="flex whitespace-nowrap" style={{ animation: 'cta-ticker 38s linear infinite' }}>
                {[0, 1].map((copy) => (
                  <span key={copy} className="flex items-center shrink-0">
                    {TICKER_ITEMS.map((item) => (
                      <span key={item} className="flex items-center gap-3 mx-5" style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, letterSpacing: '0.01em' }}>
                        <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: 9 }}>✦</span>
                        {item}
                      </span>
                    ))}
                  </span>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* Right dot-grid panel */}
        <div className="hidden md:block" aria-hidden="true" style={dotGridStyle} />

        <VerticalDash side="left" />
        <VerticalDash side="right" />

      </div>

      <DashedLine />

    </div>
  )
}
