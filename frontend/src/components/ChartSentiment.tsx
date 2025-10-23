'use client'
import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function ChartSentiment(){
  const [data] = useState<any[]>([
    {name:'neg', value:120}, {name:'neu', value:340}, {name:'pos', value:540}
  ])
  return (
    <div className="rounded-2xl bg-white p-6 shadow text-slate-900">
      <div className="text-slate-700 mb-2 font-semibold">Distribution of Sentiment (sample)</div>
      <div style={{width:'100%', height:320}}>
        <ResponsiveContainer>
          <BarChart data={data}>
            <XAxis dataKey="name" /><YAxis /><Tooltip />
            <Bar dataKey="value" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
