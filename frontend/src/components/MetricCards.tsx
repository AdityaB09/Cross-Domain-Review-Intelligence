export default function MetricCards({metrics}:{metrics:any}){
  const items = [
    {k:'val_acc_sent', label:'Sentiment'},
    {k:'val_acc_eff',  label:'Effectiveness'},
    {k:'val_acc_fx',   label:'Side-Effects'},
  ]
  return (
    <div className="grid md:grid-cols-3 gap-4">
      {items.map(i=>(
        <div key={i.k} className="rounded-2xl p-6 bg-white text-slate-900 shadow">
          <div className="text-slate-500 text-sm">{i.label}</div>
          <div className="text-3xl font-bold">{metrics[i.k] ? (metrics[i.k]*100).toFixed(1)+'%' : '—'}</div>
        </div>
      ))}
    </div>
  )
}
