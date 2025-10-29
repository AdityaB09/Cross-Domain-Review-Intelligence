"use client";

import React, { useState } from "react";
import ABSAHeatmap from "@/components/ABSAHeatmap";
import TokenAttributions from "@/components/TokenAttributions";
import { backend } from "@/lib/backend";

type AspectInfo = {
  aspect: string;
  sentiment: number;
  confidence: number;
  polarity: string;
};

type TokenInfo = {
  token: string;
  score: number;
};

export default function ExplainPage() {
  const [text, setText] = useState(
    "The pill reduced my pain fast but made me dizzy and nauseous"
  );
  const [loading, setLoading] = useState(false);
  const [aspects, setAspects] = useState<AspectInfo[]>([]);
  const [tokens, setTokens] = useState<TokenInfo[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setErr(null);
    try {
      const res = await fetch(backend("/explain-request"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) {
        setErr(`Backend ${res.status}`);
        setAspects([]);
        setTokens([]);
      } else {
        const data = await res.json();
        setAspects(Array.isArray(data.aspects) ? data.aspects : []);
        setTokens(Array.isArray(data.tokens) ? data.tokens : []);
      }
    } catch (e: any) {
      setErr("Network error talking to backend");
      setAspects([]);
      setTokens([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-5xl mx-auto px-4 py-10 space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-neutral-900">
          Explainability & ABSA
        </h1>
        <p className="text-neutral-600 max-w-2xl">
          Extract aspects (battery, charging, camera...) and see
          sentiment per aspect. Then inspect which specific words
          pushed the model positive or negative.
        </p>
      </section>

      <section className="space-y-4">
        <textarea
          className="w-full border border-neutral-300 rounded-lg p-3 text-sm"
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button
          onClick={handleRun}
          disabled={loading}
          className="bg-black text-white text-sm font-medium rounded-lg px-4 py-2 disabled:opacity-50"
        >
          {loading ? "Running..." : "Run"}
        </button>

        {err && (
          <div className="text-sm text-red-600 whitespace-pre-wrap">
            {err}
          </div>
        )}
      </section>

      <section className="grid gap-6">
        <ABSAHeatmap aspects={aspects} />

        <TokenAttributions tokens={tokens} />
      </section>
    </main>
  );
}
