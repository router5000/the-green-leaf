// Run: node --test tests/
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/isoDate.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
const { toIso8601WithOffset } = await import('data:text/javascript,' + encodeURIComponent(js))

test('adds Z to naive article generated_at timestamps', () => {
  assert.equal(toIso8601WithOffset('2026-10-07T15:31:41.236194'), '2026-10-07T15:31:41.236Z')
})

test('keeps an existing offset and normalizes to ISO', () => {
  assert.equal(toIso8601WithOffset('2026-10-07T15:31:41.236194Z'), '2026-10-07T15:31:41.236Z')
  assert.equal(toIso8601WithOffset('2026-10-07T11:31:41-04:00'), '2026-10-07T15:31:41.000Z')
})

test('date-only values get a UTC midnight offset', () => {
  assert.equal(toIso8601WithOffset('2026-10-07'), '2026-10-07T00:00:00.000Z')
})
