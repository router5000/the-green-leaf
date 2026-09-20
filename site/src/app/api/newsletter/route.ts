import { NextRequest, NextResponse } from 'next/server'
import { getSupabase } from '@/lib/supabase'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function normalizeEmail(raw: string): string {
  return raw.trim().toLowerCase()
}

export async function POST(req: NextRequest) {
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ ok: false, error: 'Invalid request' }, { status: 400 })
  }

  const emailRaw =
    typeof body === 'object' && body !== null && 'email' in body
      ? String((body as { email: unknown }).email ?? '')
      : ''
  const sourceRaw =
    typeof body === 'object' && body !== null && 'source' in body
      ? String((body as { source: unknown }).source ?? 'homepage_cta')
      : 'homepage_cta'

  // Honeypot — bots fill this; humans leave empty
  const website =
    typeof body === 'object' && body !== null && 'website' in body
      ? String((body as { website: unknown }).website ?? '')
      : ''
  if (website.trim()) {
    return NextResponse.json({ ok: true })
  }

  const email = normalizeEmail(emailRaw)
  if (!email || email.length > 320 || !EMAIL_RE.test(email)) {
    return NextResponse.json({ ok: false, error: 'Enter a valid email address' }, { status: 400 })
  }

  const source = sourceRaw.slice(0, 64) || 'homepage_cta'

  try {
    const supabase = getSupabase()
    const { error } = await supabase.from('newsletter_subscribers').insert({
      email,
      source,
    })

    if (error) {
      // Unique violation → already subscribed (treat as success)
      if (error.code === '23505') {
        return NextResponse.json({ ok: true, alreadySubscribed: true })
      }
      console.error('newsletter insert failed', error.message)
      return NextResponse.json(
        { ok: false, error: 'Could not save your email. Try again in a moment.' },
        { status: 500 }
      )
    }

    return NextResponse.json({ ok: true })
  } catch (err) {
    console.error('newsletter route error', err)
    return NextResponse.json(
      { ok: false, error: 'Newsletter is temporarily unavailable.' },
      { status: 503 }
    )
  }
}
