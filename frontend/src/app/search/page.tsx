// frontend/src/app/search/page.tsx
'use client'
import { useState } from 'react'
import { postJSON } from '../api'
import ReviewCard from '../components/ReviewCard'   // ← add this

export default function Search(){
  const [q,setQ] = useState('severe headache after taking medication, looking for similar experiences')
  const [res,setRes] = useState<any[]>([])

  async function onSearch(){
    const {results} = await postJSON('/search', {q, k: 10})
    setRes(results)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold">Find Similar Experiences</h2>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-xl p-3 text-slate-900"
          value={q}
          onChange={e=>setQ(e.target.value)}
          placeholder="Describe your experience or issue…"
        />
        <button className="rounded-xl bg-slate-900 text-white px-5" onClick={onSearch}>
          Search
        </button>
      </div>

      <div className="space-y-3">
        {res.map((r:any) => (
          <ReviewCard
            key={r.id}
            review={{
              id: r.id,
              domain: r.domain,
              product: r.product,
              text: r.text,
              rating: r.rating ?? null
            }}
          />
        ))}
      </div>
    </div>
  )
}
