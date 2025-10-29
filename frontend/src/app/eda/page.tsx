// frontend/src/app/eda/page.tsx
"use client";
import { useEffect, useState } from "react";

type Row = { aspect: string; mentions: number; avg_sentiment: number };

export default function EdaPage() {
  const [rows, setRows] = useState<Row[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/eda/aspects", { cache: "no-store" });
        if (!r.ok) throw new Error(await r.text());
        const data = await r.json();
        setRows(data.aspects ?? []);
      } catch (e: any) {
        setErr(e.message ?? "Failed to load");
      }
    })();
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Aspect Intelligence</h1>
      {err && <div className="text-sm text-red-600">{err}</div>}
      <div className="rounded border bg-white">
        <div className="grid grid-cols-3 text-xs uppercase tracking-wide text-neutral-500 border-b px-4 py-2">
          <div>Aspect</div><div className="text-right">Mentions</div><div className="text-right">Avg sentiment</div>
        </div>
        {rows.map((r, i) => (
          <div key={i} className="grid grid-cols-3 border-b last:border-b-0 px-4 py-2">
            <div className="font-medium">{r.aspect}</div>
            <div className="text-right">{r.mentions}</div>
            <div className="text-right">{r.avg_sentiment.toFixed(2)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
