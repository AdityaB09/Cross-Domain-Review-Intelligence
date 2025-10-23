// frontend/src/app/explain/page.tsx  (snippet)
'use client'
import { useState } from 'react'
import { postJSON } from '../api'
import ABSAHeatmap from '../components/ABSAHeatmap'   // ← add this

export default function Explain(){
  const [t,setT] = useState('The pill helped but gave me nausea and dizziness in the first week.')
  const [tokens,setTokens] = useState<any[]>([])
  const [aspects,setAspects] = useState<any[]>([])     // ← store ABSA here

  async function onRun(){
    // /explain returns SHAP tokens; /model/predict returns ABSA aspects
    const pred = await postJSON('/model/predict', { text: t })
    setAspects(pred.aspects || [])

    const shap = await postJSON('/explain', { text: t })
    setTokens(shap.tokens)
  }

  return (
    <div className="space-y-4">
      {/* ... existing UI ... */}
      <button className="rounded-xl bg-slate-900 text-white px-5" onClick={onRun}>Explain</button>

      {/* ABSA heatmap standalone */}
      <ABSAHeatmap aspects={aspects} />
    </div>
  )
}
