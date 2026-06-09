import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export const dynamic = 'force-dynamic'

export async function GET() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  const envCheck = {
    NEXT_PUBLIC_SUPABASE_URL_present: !!url,
    NEXT_PUBLIC_SUPABASE_URL_length: url?.length ?? 0,
    NEXT_PUBLIC_SUPABASE_URL_prefix: url?.slice(0, 30) ?? null,
    NEXT_PUBLIC_SUPABASE_ANON_KEY_present: !!key,
    NEXT_PUBLIC_SUPABASE_ANON_KEY_length: key?.length ?? 0,
    NEXT_PUBLIC_SUPABASE_ANON_KEY_prefix: key?.slice(0, 12) ?? null,
  }

  if (!url || !key) {
    return NextResponse.json({
      ok: false,
      stage: 'env',
      env: envCheck,
      error: 'Missing env vars',
    }, { status: 500 })
  }

  // Raw fetch ping — bypasses the Supabase client to verify network/auth basics
  let pingStatus: number | null = null
  let pingOk: boolean | null = null
  let pingError: string | null = null
  try {
    const pingRes = await fetch('https://nqgdqukpqutijotmfcjb.supabase.co/rest/v1/', {
      headers: { 'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '' }
    })
    pingStatus = pingRes.status
    pingOk = pingRes.ok
  } catch (e) {
    pingError = e instanceof Error ? e.message : String(e)
  }

  try {
    const supabase = createClient(url, key)

    const { count, error: countError } = await supabase
      .from('strains')
      .select('*', { count: 'exact', head: true })

    const { data: sample, error: sampleError } = await supabase
      .from('strains')
      .select('id, name, slug, published')
      .limit(3)

    const { data: publishedSample, error: publishedError } = await supabase
      .from('strains')
      .select('id, name, slug')
      .eq('published', true)
      .limit(3)

    return NextResponse.json({
      ok: !countError && !sampleError && !publishedError,
      stage: 'query',
      env: envCheck,
      pingStatus,
      pingOk,
      pingError,
      count,
      countError: countError?.message ?? null,
      sample,
      sampleError: sampleError?.message ?? null,
      publishedSample,
      publishedSampleCount: publishedSample?.length ?? 0,
      publishedError: publishedError?.message ?? null,
    })
  } catch (err) {
    return NextResponse.json({
      ok: false,
      stage: 'exception',
      env: envCheck,
      pingStatus,
      pingOk,
      pingError,
      error: err instanceof Error ? err.message : String(err),
    }, { status: 500 })
  }
}
