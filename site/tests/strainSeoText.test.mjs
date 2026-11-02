// Run: node --test tests/
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/strainSeoText.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
const { buildStrainTitle, buildStrainDescription, truncateAtWord } = await import('data:text/javascript,' + encodeURIComponent(js))

test('title format and length', () => {
  assert.equal(buildStrainTitle('Blue Dream'), 'Blue Dream Strain: Effects, THC & Review (2026)')
  assert.ok(buildStrainTitle('Blue Dream').length <= 60)
  const long = buildStrainTitle('Strawberry Banana Cheesecake')
  assert.ok(long.length <= 60, long)
  assert.ok(long.startsWith('Strawberry Banana Cheesecake Strain'))
})

const blueDream = {
  name: 'Blue Dream', strain_type: 'hybrid', thc_min: 17, thc_max: 24,
  short_description: 'Blue Dream is a sativa-dominant California hybrid crossing Blueberry and Haze, delivering balanced cerebral and body effects with sweet berry flavors. It remains popular.',
  effects: [{ effect_name: 'Euphoric', effect_type: 'positive' }, { effect_name: 'Creative', effect_type: 'positive' }, { effect_name: 'Relaxed', effect_type: 'positive' }, { effect_name: 'Dry mouth', effect_type: 'negative' }],
  terpenes: [{ terpene_name: 'Pinene', percentage: 0.2 }, { terpene_name: 'Myrcene', percentage: 0.6 }],
  flavors: ['Berry', 'Sweet'],
}
const cases = [
  blueDream,
  { ...blueDream, short_description: null },
  { ...blueDream, short_description: 'Short.', effects: [], terpenes: [], flavors: [] },
  { name: 'X', strain_type: null, short_description: null },
  { ...blueDream, short_description: 'A'.repeat(10) + ' ' + 'word '.repeat(60) },
]
test('descriptions are 140-158ish and end cleanly', () => {
  for (const c of cases) {
    const d = buildStrainDescription(c)
    assert.ok(d.length <= 158, `${d.length}: ${d}`)
    assert.match(d, /[.!?]$/, d)
    assert.doesNotMatch(d, /\.\.\.$/)
  }
  for (const c of cases.slice(0, 3)) {
    const d = buildStrainDescription(c)
    assert.ok(d.length >= 140, `${d.length}: ${d}`)
  }
})

test('truncateAtWord never splits a word', () => {
  const t = truncateAtWord('the quick brown fox jumps over the lazy dog', 17)
  assert.equal(t, 'the quick brown')
})
