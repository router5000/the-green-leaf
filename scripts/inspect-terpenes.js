#!/usr/bin/env node
// Inspect what terpene tables exist and what their schemas look like.

const fs = require('fs')
const path = require('path')

const envPath = path.join(__dirname, '..', 'site', '.env.local')
const envText = fs.readFileSync(envPath, 'utf8')
for (const line of envText.split('\n')) {
  const trimmed = line.trim()
  if (!trimmed || trimmed.startsWith('#')) continue
  const eq = trimmed.indexOf('=')
  if (eq === -1) continue
  const key = trimmed.slice(0, eq).trim()
  const val = trimmed.slice(eq + 1).trim()
  if (!(key in process.env)) process.env[key] = val
}

const url = process.env.NEXT_PUBLIC_SUPABASE_URL
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

async function probe(table) {
  console.log(`\n── ${table} ──`)
  try {
    const res = await fetch(`${url}/rest/v1/${table}?select=*&limit=3`, {
      headers: { apikey: key, Authorization: `Bearer ${key}`, Prefer: 'count=exact' },
    })
    console.log(`  status:        `, res.status)
    console.log(`  content-range: `, res.headers.get('content-range'))
    const body = await res.text()
    console.log(`  body:          `, body.length > 800 ? body.slice(0, 800) + '...' : body)
  } catch (e) {
    console.log('  ERROR:', e.message)
  }
}

async function probeName(table, column, value) {
  console.log(`\n── ${table} where ${column}=${value} (count) ──`)
  try {
    const res = await fetch(
      `${url}/rest/v1/${table}?select=${column}&${column}=eq.${encodeURIComponent(value)}`,
      { headers: { apikey: key, Authorization: `Bearer ${key}`, Prefer: 'count=exact' } },
    )
    console.log(`  status:        `, res.status)
    console.log(`  content-range: `, res.headers.get('content-range'))
  } catch (e) {
    console.log('  ERROR:', e.message)
  }
}

;(async () => {
  await probe('terpenes')
  await probe('strain_terpenes')
  // Try a few likely terpene name values in both possible tables/columns
  await probeName('terpenes',        'terpene_name', 'myrcene')
  await probeName('terpenes',        'terpene_name', 'Myrcene')
  await probeName('terpenes',        'name',         'myrcene')
  await probeName('strain_terpenes', 'name',         'myrcene')
  await probeName('strain_terpenes', 'terpene_name', 'myrcene')
})()
