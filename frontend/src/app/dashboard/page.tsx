'use client'
import { useEffect, useState } from 'react'
import { getJSON } from '../api'
import MetricCards from '../components/MetricCards'
import ChartSentiment from '../components/ChartSentiment'

export default function Dashboard(){
  const [m,setM] = useState<any>(null)
  useEffect(()=>{ getJSON('/eval/metrics').then(setM).catch(console.error) },[])
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Model Overview</h2>
      <MetricCards metrics={m || {}} />
      <ChartSentiment />
    </div>
  )
}
