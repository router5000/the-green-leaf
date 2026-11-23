// Run: node --test tests/
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import ts from 'typescript'

const src = readFileSync(new URL('../src/lib/articleTitle.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
const { articleDocumentTitle } = await import('data:text/javascript,' + encodeURIComponent(js))

test('appends a single site suffix', () => {
  assert.equal(
    articleDocumentTitle('Blue Dream Strain Effects & Review (2026)'),
    'Blue Dream Strain Effects & Review (2026) - The Strain Report',
  )
})

test('strips an existing | or - site suffix instead of doubling it', () => {
  assert.equal(
    articleDocumentTitle('Cannabis Hash Types Explained | The Strain Report'),
    'Cannabis Hash Types Explained - The Strain Report',
  )
  assert.equal(
    articleDocumentTitle('Cannabis Hash Types Explained - The Strain Report'),
    'Cannabis Hash Types Explained - The Strain Report',
  )
  assert.equal(
    articleDocumentTitle('Cannabis Hash Types Explained | The Strain Report - The Strain Report'),
    'Cannabis Hash Types Explained - The Strain Report',
  )
})

test('every post frontmatter title becomes a non-doubled document title', () => {
  const postsDir = fileURLToPath(new URL('../content/posts', import.meta.url))
  const files = readdirSync(postsDir).filter((f) => f.endsWith('.md'))
  assert.ok(files.length > 0, 'expected article posts')
  const doubled = /\s*[-–—|]\s*The Strain Report\s*[-–—|]\s*The Strain Report\s*$/i
  for (const f of files) {
    const text = readFileSync(path.join(postsDir, f), 'utf8')
    const m = text.match(/^title:\s*"([^"]+)"/m)
    assert.ok(m, `missing title in ${f}`)
    const doc = articleDocumentTitle(m[1])
    assert.ok(!doubled.test(doc), `${f}: doubled suffix: ${doc}`)
    assert.match(doc, / - The Strain Report$/)
  }
})
