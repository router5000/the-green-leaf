'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { TIER_BADGE, TIER_LABEL, TIER_ORDER, type CompareRow, type StatusTier } from '@/data/statesCompare'

type SortKey = 'name' | 'tier' | 'minimumAge' | 'salesOpen'

export default function CompareTable({ rows }: { rows: CompareRow[] }) {
  const [tier, setTier] = useState<StatusTier | 'all'>('all')
  const [q, setQ] = useState('')
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: 'name', dir: 1 })

  const visible = useMemo(() => {
    const needle = q.trim().toLowerCase()
    const out = rows.filter(r =>
      (tier === 'all' || r.tier === tier) &&
      (!needle || r.name.toLowerCase().includes(needle) || r.homeGrow.toLowerCase().includes(needle) || r.possessionLimit.toLowerCase().includes(needle)))
    const val = (r: CompareRow): string | number =>
      sort.key === 'name' ? r.name : sort.key === 'tier' ? TIER_ORDER[r.tier] : sort.key === 'minimumAge' ? (r.minimumAge ?? 99) : (r.salesOpen ? 0 : 1)
    return [...out].sort((a, b) => {
      const va = val(a), vb = val(b)
      const c = va < vb ? -1 : va > vb ? 1 : a.name.localeCompare(b.name)
      return c * sort.dir
    })
  }, [rows, tier, q, sort])

  const counts = useMemo(() => {
    const c: Record<string, number> = { all: rows.length }
    rows.forEach(r => { c[r.tier] = (c[r.tier] || 0) + 1 })
    return c
  }, [rows])

  const header = (key: SortKey, label: string) => {
    const active = sort.key === key
    return (
      <button
        type="button"
        onClick={() => setSort(s => ({ key, dir: s.key === key ? (s.dir === 1 ? -1 : 1) : 1 }))}
        className="inline-flex items-center gap-1 font-semibold hover:text-leaf-700"
        aria-label={`Sort by ${label}`}
      >
        {label}
        <span aria-hidden="true" className="text-neutral-400">{active ? (sort.dir === 1 ? '▲' : '▼') : '↕'}</span>
      </button>
    )
  }
  const ariaSort = (key: SortKey) => (sort.key === key ? (sort.dir === 1 ? 'ascending' : 'descending') : 'none')

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center gap-3 mb-4">
        <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by legal status">
          {(['all', 'recreational', 'medical', 'cbd-only', 'illegal'] as const).map(t => (
            <button
              key={t}
              type="button"
              onClick={() => setTier(t)}
              aria-pressed={tier === t}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                tier === t ? 'bg-[#1a3a0a] text-white' : 'bg-white text-neutral-700 shadow-sm hover:bg-neutral-50'
              }`}
            >
              {t === 'all' ? 'All' : TIER_LABEL[t]}
              <span className="ml-1.5 text-xs opacity-60">{counts[t] || 0}</span>
            </button>
          ))}
        </div>
        <label className="md:ml-auto">
          <span className="sr-only">Search states</span>
          <input
            type="search"
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Search state or rule…"
            className="w-full md:w-64 px-4 py-2 rounded-full bg-white shadow-sm text-sm outline-none focus:ring-2 focus:ring-leaf-500"
          />
        </label>
      </div>

      <p className="text-xs text-neutral-500 mb-2" aria-live="polite">Showing {visible.length} of {rows.length} states</p>

      <div className="bg-white rounded-xl shadow-sm overflow-x-auto">
        <table className="min-w-[1100px] w-full text-sm text-left border-collapse">
          <caption className="sr-only">Cannabis laws by US state: legal status, possession limit, home grow, minimum age, dispensary sales, public use, and last reviewed date</caption>
          <thead className="bg-neutral-50 text-neutral-700">
            <tr>
              <th scope="col" aria-sort={ariaSort('name')} className="sticky left-0 z-10 bg-neutral-50 px-4 py-3 min-w-[140px] border-r border-neutral-200">{header('name', 'State')}</th>
              <th scope="col" aria-sort={ariaSort('tier')} className="px-4 py-3 min-w-[150px]">{header('tier', 'Status')}</th>
              <th scope="col" className="px-4 py-3 min-w-[200px] font-semibold">Possession limit</th>
              <th scope="col" className="px-4 py-3 min-w-[200px] font-semibold">Home grow</th>
              <th scope="col" aria-sort={ariaSort('minimumAge')} className="px-4 py-3 min-w-[90px]">{header('minimumAge', 'Min. age')}</th>
              <th scope="col" aria-sort={ariaSort('salesOpen')} className="px-4 py-3 min-w-[110px]">{header('salesOpen', 'Sales open?')}</th>
              <th scope="col" className="px-4 py-3 min-w-[260px] font-semibold">Public use</th>
              <th scope="col" className="px-4 py-3 min-w-[110px] font-semibold">Last reviewed</th>
            </tr>
          </thead>
          <tbody>
            {visible.map(r => (
              <tr key={r.slug} className="border-t border-neutral-100 align-top hover:bg-neutral-50/60 group">
                <th scope="row" className="sticky left-0 z-10 bg-white group-hover:bg-neutral-50 px-4 py-3 font-semibold border-r border-neutral-200">
                  <Link href={`/states/${r.slug}`} className="text-neutral-900 hover:text-leaf-700 underline-offset-2 hover:underline">{r.name}</Link>
                </th>
                <td className="px-4 py-3">
                  <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${TIER_BADGE[r.tier]}`}>{TIER_LABEL[r.tier]}</span>
                </td>
                <td className="px-4 py-3 text-neutral-700">{r.possessionLimit}</td>
                <td className="px-4 py-3 text-neutral-700">{r.homeGrow}</td>
                <td className="px-4 py-3 text-neutral-700">{r.minimumAge ? `${r.minimumAge}+` : '—'}</td>
                <td className="px-4 py-3">
                  <span className={r.salesOpen ? 'text-leaf-700 font-medium' : 'text-red-600 font-medium'}>{r.salesOpen ? 'Yes' : 'No'}</span>
                </td>
                <td className="px-4 py-3 text-neutral-600">{r.publicUse}</td>
                <td className="px-4 py-3 text-neutral-500 whitespace-nowrap">{r.lastReviewed}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
