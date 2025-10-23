'use client'
/**
 * Visualizes ABSA results as a compact heatmap-like bar list.
 * Each aspect shows a 3-cell bar: [NEG | NEU | POS] with intensity by score.
 * Input shape matches backend: { aspect, polarity, scores: [neg, neu, pos] }.
 */

type AspectItem = {
  aspect: string
  polarity: 'neg'|'neu'|'pos'
  scores: number[] // length 3: [neg, neu, pos], softmax probs
}

export default function ABSAHeatmap({aspects}:{aspects: AspectItem[]}) {
  if (!aspects?.length) {
    return (
      <div className="rounded-xl border border-slate-200 p-3 text-sm text-slate-600 bg-slate-50">
        No aspects detected.
      </div>
    )
  }

  const clamp01 = (x:number) => Math.max(0, Math.min(1, x))

  const cell = (v:number, label:string, tone:'neg'|'neu'|'pos') => {
    const alpha = clamp01(v) // assume 0..1
    const color = tone === 'neg'
      ? `rgba(239,68,68,${alpha})`     // red-500
      : tone === 'pos'
      ? `rgba(34,197,94,${alpha})`     // green-500
      : `rgba(100,116,139,${alpha})`   // slate-500
    return (
      <div className="flex-1 h-6 rounded" style={{ background: color }} title={`${label}: ${(v*100).toFixed(1)}%`} />
    )
  }

  return (
    <div className="rounded-2xl border border-slate-200 p-4 bg-white">
      <div className="mb-3 flex items-center justify-between">
        <div className="font-semibold text-slate-800">Aspect Sentiment (ABSA)</div>
        <div className="flex items-center gap-3 text-xs text-slate-600">
          <span className="inline-flex items-center gap-1"><i className="w-3 h-3 rounded-sm" style={{background:'rgba(239,68,68,0.8)'}}></i>NEG</span>
          <span className="inline-flex items-center gap-1"><i className="w-3 h-3 rounded-sm" style={{background:'rgba(100,116,139,0.8)'}}></i>NEU</span>
          <span className="inline-flex items-center gap-1"><i className="w-3 h-3 rounded-sm" style={{background:'rgba(34,197,94,0.8)'}}></i>POS</span>
        </div>
      </div>

      <div className="space-y-3">
        {aspects.map((a, i) => (
          <div key={i} className="grid grid-cols-12 items-center gap-3">
            <div className="col-span-3 md:col-span-2">
              <div className="truncate text-sm font-medium text-slate-800" title={a.aspect}>{a.aspect}</div>
              <div className="text-[11px] uppercase tracking-wide text-slate-500">pred: {a.polarity}</div>
            </div>
            <div className="col-span-9 md:col-span-10">
              <div className="flex gap-1">
                {cell(a.scores?.[0] ?? 0, 'neg', 'neg')}
                {cell(a.scores?.[1] ?? 0, 'neu', 'neu')}
                {cell(a.scores?.[2] ?? 0, 'pos', 'pos')}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
