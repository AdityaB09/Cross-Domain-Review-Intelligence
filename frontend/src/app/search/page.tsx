'use client'

import { useState } from 'react'
import { postJSON } from '../api'
import ReviewCard, { Review } from '../components/ReviewCard'

type Hit = {
  id: string
  text: string
  score?: number
  domain?: string
  product?: string
  date?: string
}

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [res, setRes] = useState<Hit[]>([])
  const [loading, setLoading] = useState(false)
  const [ran, setRan] = useState(false)

  async function onSearch() {
    if (!q.trim()) return
    setLoading(true)
    try {
      // NOTE: backend must have POST /search -> { results: Hit[] }
      const r = await postJSON<{ results: Hit[] }>('/search', { q, k: 10 })
      setRes(r?.results || [])
      setRan(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mx-auto max-w-3xl space-y-8">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-bold text-gray-900">Semantic Search</h1>
        <p className="text-sm text-gray-600">
          Describe an experience or complaint. We’ll find similar real reviews.
          (Make sure you’ve ingested data and run /build.)
        </p>
      </header>

      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          className="flex-1 rounded-xl border border-gray-300 bg-white p-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-black/20"
          placeholder="Describe an experience or side-effect…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button
          onClick={onSearch}
          disabled={loading}
          className="rounded-xl bg-black px-4 py-2 text-white shadow-sm disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="grid gap-4">
        {res.map((h) => {
          const review: Review = {
            text: h.text,
            score:
              typeof h.score === 'number'
                ? Math.max(0, Math.min(1, h.score))
                : undefined,
            meta: {
              domain: h.domain,
              product: h.product,
              date: h.date,
            },
          }
          return <ReviewCard key={h.id} review={review} />
        })}

        {!loading && ran && res.length === 0 && (
          <div className="text-gray-500 text-sm">
            No results yet. Try different wording, or rebuild the index.
          </div>
        )}

        {!ran && !res.length && (
          <div className="text-gray-500 text-sm">No results yet.</div>
        )}
      </div>
    </section>
  )
}
