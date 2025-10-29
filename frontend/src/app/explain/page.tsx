// frontend/src/app/explain/page.tsx
"use client";
import { useState } from "react";

type Aspect = { aspect: string; sentiment: number; confidence: number };

export default function ExplainPage() {
  const [text, setText] = useState("");
  const [aspects, setAspects] = useState<Aspect[]>([]);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setAspects([]);
    const r = await fetch("/api/explain-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await r.json();
    setAspects(data.aspects ?? []);
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Explain (ABSA)</h1>
      <textarea className="w-full border rounded p-3" rows={4}
        placeholder="The camera is amazing but the speaker crackles and it overheats"
        value={text} onChange={e=>setText(e.target.value)} />
      <button onClick={run} className="px-4 py-2 rounded bg-black text-white">
        {loading ? "Explaining..." : "Explain"}
      </button>

      {aspects.length > 0 && (
        <div className="rounded border bg-white">
          {aspects.map((a, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-2 border-b last:border-b-0">
              <div className="font-medium">{a.aspect}</div>
              <div className="text-sm">
                {a.sentiment.toFixed(2)} ({a.sentiment > 0 ? "positive" : "negative"})
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
