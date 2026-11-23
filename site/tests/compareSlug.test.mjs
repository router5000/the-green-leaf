// Run: node --test tests/   (transpiles the TS helper with the repo's typescript)
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/compareSlug.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
const {
  parseCompareSlug,
  canonicalCompareSlug,
  comparePath,
  canonicalizeCompareSlug,
} = await import('data:text/javascript,' + encodeURIComponent(js))

test('canonical slug is alphabetical', () => {
  assert.equal(canonicalCompareSlug('blue-dream', 'og-kush'), 'blue-dream-vs-og-kush')
  assert.equal(canonicalCompareSlug('og-kush', 'blue-dream'), 'blue-dream-vs-og-kush')
  assert.equal(canonicalCompareSlug('sour-diesel', 'blue-dream'), 'blue-dream-vs-sour-diesel')
  assert.equal(canonicalCompareSlug('a', 'a'), 'a-vs-a')
})

test('comparePath uses the canonical slug', () => {
  assert.equal(comparePath('og-kush', 'blue-dream'), '/strains/compare/blue-dream-vs-og-kush')
  assert.equal(comparePath('blue-dream', 'og-kush'), '/strains/compare/blue-dream-vs-og-kush')
})

test('parseCompareSlug requires two distinct sides', () => {
  assert.deepEqual(parseCompareSlug('blue-dream-vs-og-kush'), ['blue-dream', 'og-kush'])
  assert.equal(parseCompareSlug('blue-dream'), null)
  assert.equal(parseCompareSlug('blue-dream-vs-'), null)
  assert.equal(parseCompareSlug('blue-dream-vs-blue-dream'), null)
  assert.equal(parseCompareSlug('a-vs-b-vs-c'), null)
})

test('canonicalizeCompareSlug flips the reverse and leaves the canonical alone', () => {
  assert.equal(canonicalizeCompareSlug('og-kush-vs-blue-dream'), 'blue-dream-vs-og-kush')
  assert.equal(canonicalizeCompareSlug('blue-dream-vs-og-kush'), 'blue-dream-vs-og-kush')
  assert.equal(canonicalizeCompareSlug('not-a-pair'), null)
})
