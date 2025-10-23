'use client'
import { useState } from 'react'
import { postJSON } from '../../api'
import ABSAHeatmap from './ABSAHeatmap'

type Review = {
  id?: number
  domain: string
  product: string
  text: string
  rating?: number | null
}

type PredictOut = {
  sentiment: 'neg'|'neu'|'pos'
  effectiveness: 'low'|'med'|'high'
  side_effects: string[]
  aspects?: { aspect: string; polarity: 'neg'|'neu'|'pos'; scores: number[] }[]
}

function Badge({children, tone='slate'}:{children: React.ReactNode; tone?: 'green'|'red'|'slate'|'amber'|'blue'}) {
  const tones: Record<string,string> = {
    green: 'bg-green-100 text-green-800',
    red: 'bg-red-100 text-red-800',
    slate: 'bg-slate-100 text-slate-800',
    amber: 'bg-amber-100 text-amber-900',
    blue: 'bg-blue-100 text-blue-800',
  }
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${tones[tone] || tones.slate}`}>{children}</span>
}

export default function ReviewCard({review}:{review: Review}) {
  const [loading, setLoading] = useState(false)
  const [pred, setPred] = useState<PredictOut | null>(null)
  const [err, setErr] = useState<string | null>(null)

  const run = async () => {
    try {
      setLoading(true); setErr(null)
      const out = await postJSON<PredictOut>('/model/predict', { text: review.text })
      setPred(out)
    } catch (e:any) {
      setErr(e?.message || 'Failed to analyze')
    } finally {
      setLoading(false)
    }
  }

  const toneBySent: Record<string,'red'|'slate'|'green'> = { neg:'red', neu:'slate', pos:'green' }
  const toneByEff: Record<string,'red'|'amber'|'green'> = { low:'red', med:'amber', high:'green' }

  return (
    <div className="rounded-2xl bg-white p-5 shadow text-slate-900 space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div className="text-xs uppercase text-slate-500">
          {review.domain} • {review.product}
          {typeof review.rating === 'number' && (
            <span className="ml-2 text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
              ★ {review.rating.toFixed(1)}
            </span>
          )}
        </div>
        <button
          onClick={run}
          disabled={loading}
          className="rounded-xl bg-slate-900 text-white px-4 py-1.5 text-sm disabled:opacity-60"
          title="Analyze with multi-label model + ABSA"
        >
          {loading ? 'Analyzing…' : (pred ? 'Re-analyze' : 'Analyze')}
        </button>
      </div>

      <p className="leading-relaxed">{review.text}</p>

      {err && <div className="text-sm text-red-700">{err}</div>}

      {pred && (
        <>
          <div className="flex flex-wrap gap-2 pt-2">
            <Badge tone={toneBySent[pred.sentiment]}>Sentiment: {pred.sentiment}</Badge>
            <Badge tone={toneByEff[pred.effectiveness]}>Effectiveness: {pred.effectiveness}</Badge>
            {pred.side_effects?.length ? (
              <Badge tone="blue">Side-effects: {pred.side_effects.join(', ')}</Badge>
            ) : (
              <Badge>Side-effects: none</Badge>
            )}
          </div>

          <div className="pt-3">
            <ABSAHeatmap aspects={pred.aspects || []} />
          </div>
        </>
      )}
    </div>
  )
}
