import { createClient } from '@supabase/supabase-js'

let client: ReturnType<typeof createClient> | null = null

export function getSupabase() {
  if (!client) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    if (!url || !key) throw new Error('Supabase env vars not set')
    client = createClient(url, key)
  }
  return client
}
