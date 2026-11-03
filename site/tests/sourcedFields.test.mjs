// Run: node --test tests/
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/sourcedFields.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
const { hideUnsourced } = await import('data:text/javascript,' + encodeURIComponent(js))

const base = {
  name: 'X', flowering_time_days: 62, yield_indoor: '1.5-2 oz/ft²', yield_outdoor: '14-18 oz/plant',
  height_indoor: 'Medium', height_outdoor: 'Tall', difficulty: 'moderate',
  terpenes: [{ terpene_name: 'Myrcene', percentage: 0.5 }],
}

test('hides grow fields and terpene % with no sources', () => {
  const r = hideUnsourced({ ...base, strain_sources: [] })
  for (const f of ['flowering_time_days', 'yield_indoor', 'yield_outdoor', 'height_indoor', 'height_outdoor', 'difficulty'])
    assert.equal(r[f], null, f)
  assert.equal(r.terpenes[0].percentage, null)
  assert.equal(r.terpenes[0].terpene_name, 'Myrcene')
  assert.equal(base.yield_indoor, '1.5-2 oz/ft²') // input not mutated
})

test('keeps backed fields', () => {
  const r = hideUnsourced({ ...base, strain_sources: [{ field: 'yield_indoor' }, { field: 'terpene_pct' }, { field: 'description' }] })
  assert.equal(r.yield_indoor, '1.5-2 oz/ft²')
  assert.equal(r.flowering_time_days, null)
  assert.equal(r.terpenes[0].percentage, 0.5)
})

test('missing embed = unsourced', () => {
  assert.equal(hideUnsourced({ ...base }).difficulty, null)
})
