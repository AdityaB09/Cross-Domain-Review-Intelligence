'use client'
import { useEffect, useState } from 'react'
import { getJSON } from '../api'
import MetricCards from '../components/MetricCards'
import ChartSentiment, { Point } from '../components/ChartSentiment'

export default function DashboardPage(){
  const [m, setM] = useState<Record<string, any>>({})
  const [series, setSeries] = useState<Point[]>([])

  useEffect(() => {
    // optional: load basic metrics
    getJSON('/metrics').then((x) => setM(x?.data || {})).catch(() => {})
    // simple demo line
    setSeries([
      { x: 'Mon', y: -0.2 },
      { x: 'Tue', y: 0.1 },
      { x: 'Wed', y: 0.3 },
      { x: 'Thu', y: -0.1 },
      { x: 'Fri', y: 0.5 },
    ])
  }, [])

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-3xl font-bold">Model Overview</h2>
      <MetricCards metrics={m || {}} />
      <ChartSentiment data={series} />
    </div>
  )
}
