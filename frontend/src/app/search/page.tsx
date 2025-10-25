'use client'
import { useState } from 'react'
import { postJSON } from '../api'
import ReviewCard, { Review } from '../components/ReviewCard'

type Hit = { id: string; text: string; score?: number; domain?: string; product?: string; date?: string }

export default function SearchPage(){
  const [q, setQ] = useState('')
  const [res, setRes] = useState<Hit[]>([])
  const [loading, setLoading] = useState(false)

  async function onSearch(){
    setLoading(true)
    try {
      const r = await postJSON<{ results: Hit[] }>('/search', { q, k: 10 })
      setRes(r?.results || [])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Semantic Search</h1>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded-xl border p-3"
          placeholder="Describe an experience or side-effect…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button onClick={onSearch} className="rounded-xl bg-black text-white px-4 py-2">Search</button>
      </div>

      <div className="grid gap-4">
        {res.map((h) => {
          const review: Review = {
            text: h.text,
            score: typeof h.score === "number" ? Math.max(0, Math.min(1, h.score)) : undefined,
            meta: { domain: h.domain, product: h.product, date: h.date }
          }
          return <ReviewCard key={h.id} review={review} />
        })}
        {!loading && !res.length && <div className="text-gray-500">No results yet.</div>}
      </div>
    </div>
  )
}
