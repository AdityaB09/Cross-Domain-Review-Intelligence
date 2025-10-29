// frontend/src/app/search/page.tsx
"use client";
import { useState } from "react";

type Hit = { id: number; domain: string; product: string; text: string; score: number };

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Hit[]>([]);
  const [loading, setLoading] = useState(false);

  async function runSearch() {
    setLoading(true);
    try {
      const r = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q, k: 10 }),
      });
      const data = await r.json();
      setRows(data.hits ?? []);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Search</h1>
      <div className="flex gap-2">
        <input className="border rounded px-3 py-2 w-full" value={q}
          onChange={e=>setQ(e.target.value)} placeholder="camera sharp but speaker crackles" />
        <button onClick={runSearch} className="px-4 py-2 rounded bg-black text-white">
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
      <div className="space-y-3">
        {rows.map((h) => (
          <div key={h.id} className="rounded border p-3 bg-white">
            <div className="text-xs text-neutral-500">{h.domain} • {h.product} • score {h.score.toFixed(3)}</div>
            <div>{h.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
