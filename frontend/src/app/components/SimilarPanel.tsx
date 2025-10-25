export default function SimilarPanel({items}:{items:any[]}){
  return (
    <div className="space-y-3">
      {items.map((r)=>(
        <div key={r.id} className="rounded-2xl bg-white p-4 shadow text-slate-900">
          <div className="text-xs uppercase text-slate-500">{r.domain} • {r.product}</div>
          <p className="mt-1">{r.text}</p>
        </div>
      ))}
    </div>
  )
}
