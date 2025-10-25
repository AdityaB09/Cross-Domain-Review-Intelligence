'use client'
import { useState } from 'react';
import { postJSON } from '../api';
import ABSAHeatmap, { AspectItem } from '../components/ABSAHeatmap';

type TokenAttr = { token: string; attribution: number };

export default function ExplainPage() {
  const [t, setT] = useState("");
  const [tokens, setTokens] = useState<TokenAttr[]>([]);
  const [aspects, setAspects] = useState<AspectItem[]>([]);

  async function run() {
    // ABSA-like output
    const pred = await postJSON<{ aspects?: AspectItem[] }>('/model/predict', { text: t });
    setAspects(pred.aspects || []);
    // SHAP-ish token attribution demo
    const shap = await postJSON<{ tokens: TokenAttr[] }>('/explain', { text: t });
    setTokens(shap.tokens || []);
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Explainability & ABSA</h1>
      <textarea
        className="w-full rounded-xl border p-4 min-h-[120px]"
        placeholder="Paste a review…"
        value={t}
        onChange={(e) => setT(e.target.value)}
      />
      <button onClick={run} className="rounded-xl bg-black text-white px-4 py-2">Run</button>

      <div className="rounded-2xl border bg-white p-4 shadow-sm">
        <h3 className="font-semibold text-lg mb-2">Aspect Heatmap</h3>
        <ABSAHeatmap aspects={aspects} />
      </div>

      <div className="rounded-2xl border bg-white p-4 shadow-sm">
        <h3 className="font-semibold text-lg mb-2">Token attributions</h3>
        <div className="flex flex-wrap gap-2">
          {tokens.map((tk, i) => {
            const opacity = Math.min(0.9, Math.max(0.1, Math.abs(tk.attribution)));
            const bg = tk.attribution >= 0 ? `rgba(34,197,94,${opacity})` : `rgba(239,68,68,${opacity})`;
            return (
              <span key={`${tk.token}-${i}`} className="px-2 py-1 rounded" style={{ background: bg }}>
                {tk.token}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}
