// Run: node --test tests/   (transpiles the TS helper with the repo's typescript)
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/contentDates.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
}).outputText
const { strainContentUpdatedAt, formatContentDate, latestDate } = await import(
  'data:text/javascript,' + encodeURIComponent(js)
)

test('hides seed-only dates (created ≈ updated)', () => {
  assert.equal(
    strainContentUpdatedAt({
      created_at: '2026-06-13T01:24:54.273602+00:00',
      updated_at: '2026-06-13T01:24:54.273602+00:00',
    }),
    null,
  )
  assert.equal(
    strainContentUpdatedAt({
      created_at: '2026-06-13T01:24:54.000Z',
      updated_at: '2026-06-13T01:25:10.000Z', // within 60s
    }),
    null,
  )
})

test('returns ISO when content was rewritten after seed', () => {
  const iso = strainContentUpdatedAt({
    created_at: '2026-06-13T01:24:54.273602+00:00',
    updated_at: '2026-11-08T17:24:35.554723+00:00',
  })
  assert.equal(iso, '2026-11-08T17:24:35.554Z')
  assert.equal(formatContentDate(iso), 'November 8, 2026')
})

test('missing updated_at is not trustworthy', () => {
  assert.equal(strainContentUpdatedAt({ created_at: '2026-06-13T01:24:54Z', updated_at: null }), null)
  assert.equal(strainContentUpdatedAt({}), null)
})

test('updated_at alone (no created_at) is accepted', () => {
  const iso = strainContentUpdatedAt({ updated_at: '2026-11-08T17:24:35.554Z' })
  assert.equal(iso, '2026-11-08T17:24:35.554Z')
})

test('latestDate still picks the newest input', () => {
  const d = latestDate('2026-01-01', '2026-11-08T17:24:35.554Z', null)
  assert.equal(d.toISOString(), '2026-11-08T17:24:35.554Z')
})
