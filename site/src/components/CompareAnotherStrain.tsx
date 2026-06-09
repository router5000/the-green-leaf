'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'

type Props = {
  slugs: { slug: string; name: string }[]
  currentSlugA?: string
  currentSlugB?: string
}

export default function CompareAnotherStrain({ slugs, currentSlugA = '', currentSlugB = '' }: Props) {
  const router = useRouter()
  const [a, setA] = useState(currentSlugA)
  const [b, setB] = useState(currentSlugB)

  const slugSet = new Set(slugs.map((s) => s.slug))

  function resolveSlug(input: string): string | null {
    const trimmed = input.trim().toLowerCase()
    if (!trimmed) return null
    if (slugSet.has(trimmed)) return trimmed
    // Allow entering the display name
    const match = slugs.find((s) => s.name.toLowerCase() === trimmed)
    return match ? match.slug : null
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const sa = resolveSlug(a)
    const sb = resolveSlug(b)
    if (!sa || !sb || sa === sb) return
    router.push(`/strains/compare/${sa}-vs-${sb}`)
  }

  return (
    <form onSubmit={onSubmit} className="bg-white rounded-xl border border-gray-200 p-6 mt-12">
      <h2 className="font-serif text-xl text-gray-900 mb-4">Compare another pair</h2>
      <datalist id="strain-slug-list">
        {slugs.map((s) => (
          <option key={s.slug} value={s.slug}>{s.name}</option>
        ))}
      </datalist>
      <div className="grid sm:grid-cols-[1fr_auto_1fr_auto] gap-3 items-center">
        <input
          list="strain-slug-list"
          value={a}
          onChange={(e) => setA(e.target.value)}
          placeholder="First strain (e.g. blue-dream)"
          aria-label="First strain"
          className="px-4 py-2.5 rounded-full border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-leaf-500"
        />
        <span className="text-gray-400 font-medium text-sm hidden sm:block">vs</span>
        <input
          list="strain-slug-list"
          value={b}
          onChange={(e) => setB(e.target.value)}
          placeholder="Second strain (e.g. og-kush)"
          aria-label="Second strain"
          className="px-4 py-2.5 rounded-full border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-leaf-500"
        />
        <button
          type="submit"
          className="px-5 py-2.5 rounded-full bg-leaf-600 text-white text-sm font-medium hover:bg-leaf-700 transition-colors whitespace-nowrap"
        >
          Compare →
        </button>
      </div>
    </form>
  )
}
