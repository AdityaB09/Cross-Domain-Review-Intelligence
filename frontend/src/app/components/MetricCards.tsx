"use client";
type MetricMap = Record<string, number | string>;

export default function MetricCards({ metrics }: { metrics: MetricMap }) {
  const entries = Object.entries(metrics || {});
  if (!entries.length) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl border bg-white p-4 shadow-sm">
            <div className="text-sm text-gray-500">Metric</div>
            <div className="text-2xl font-semibold">—</div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {entries.map(([k, v]) => (
        <div key={k} className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="text-sm text-gray-500">{k}</div>
          <div className="text-2xl font-semibold">{String(v)}</div>
        </div>
      ))}
    </div>
  );
}
