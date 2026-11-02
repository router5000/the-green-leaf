// Run: node --test tests/   (transpiles the TS helper with the repo's typescript)
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/formatRange.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
const { formatPctRange, describePctRange } = await import('data:text/javascript,' + encodeURIComponent(js))

test('collapses equal min/max', () => {
  assert.equal(formatPctRange(21, 21), '21%')
  assert.equal(formatPctRange(20, 20), '20%')
  assert.equal(formatPctRange(18, 18, { sep: '-' }), '18%')
})
test('renders a real range', () => {
  assert.equal(formatPctRange(18, 22), '18–22%')
  assert.equal(formatPctRange(22, 18), '18–22%')
  assert.equal(formatPctRange(0.1, 1, { sep: '-' }), '0.1-1%')
})
test('single value or none', () => {
  assert.equal(formatPctRange(null, 21), '21%')
  assert.equal(formatPctRange(21, undefined), '21%')
  assert.equal(formatPctRange(null, null), null)
})
test('sentence form', () => {
  assert.equal(describePctRange(21, 21), '21%')
  assert.equal(describePctRange(18, 22), 'between 18% and 22%')
})
