"use client";

import ABSAHeatmap, { AspectItem } from "@/components/ABSAHeatmap";
import TokenAttributions from "@/components/TokenAttributions";
import { useState } from "react";

export default function ExplainPage() {
  const [text, setText] = useState(
    "The pill reduced my pain fast but made me dizzy and nauseous"
  );

  // use the shared type now:
  const [aspects, setAspects] = useState<AspectItem[]>([]);

  const [tokens, setTokens] = useState<{ token: string; score: number }[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleRun() {
    try {
      setLoading(true);

      const resp = await fetch("/api/explain-request", {
        method: "POST",
        body: JSON.stringify({ text }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!resp.ok) {
        console.error("Explain API error:", resp.statusText);
        return;
      }

      const data = await resp.json();

      // assume backend returns { aspects: [...], tokens: [...] }
      setAspects(
        (data.aspects || []).map((a: any) => ({
          aspect: a.aspect,
          sentiment: a.sentiment,
          confidence: a.confidence,
          polarity: a.polarity, // might be undefined, that's okay now
        }))
      );

      setTokens(data.tokens || []);
      
    } catch (err) {
      console.error("Failed to run explain:", err);
    } finally {
      setLoading(false);
    }
  }
  return (
    <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <header className="text-center space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
          Explainability &amp; ABSA
        </h1>
        <p className="text-neutral-600 text-sm leading-relaxed max-w-3xl mx-auto">
          Extract aspects (battery, charging, camera…) and see sentiment per
          aspect. Then inspect which specific words pushed the model positive or
          negative.
        </p>
      </header>

      {/* Input box + Run */}
      <section className="space-y-4">
        <textarea
          className="w-full border border-neutral-300 rounded-md p-4 text-[15px] leading-relaxed focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          onClick={handleRun}
          disabled={loading}
          className="inline-flex items-center rounded-md bg-black text-white px-4 py-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Running..." : "Run"}
        </button>
      </section>

      {/* Aspect Heatmap */}
      <section className="border border-neutral-200 rounded-xl p-5 bg-white shadow-sm">
        <h2 className="text-lg font-semibold text-neutral-900 mb-1">
          Aspect Heatmap
        </h2>
        <p className="text-neutral-600 text-sm mb-4 max-w-2xl">
          For each detected aspect (like “the speaker” or “my back pain”), we
          estimate sentiment and confidence. Think of this as aspect-based
          sentiment.
        </p>

        {aspects.length === 0 ? (
          <p className="text-sm text-neutral-500">
            No aspects detected yet. Paste a review and click Run.
          </p>
        ) : (
          <ABSAHeatmap aspects={aspects} />
        )}
      </section>

      {/* Token attributions */}
      <section className="border border-neutral-200 rounded-xl p-5 bg-white shadow-sm">
        <h2 className="text-lg font-semibold text-neutral-900 mb-1">
          Token attributions
        </h2>
        <p className="text-neutral-600 text-sm mb-4 max-w-2xl">
          These tokens most influenced the model. Red tokens pulled sentiment
          negative, green pulled sentiment positive. The small number on each
          token is its contribution strength.
        </p>

        {tokens.length === 0 ? (
          <p className="text-sm text-neutral-500">
            No attributions yet. Paste a review and click Run.
          </p>
        ) : (
          <TokenAttributions tokens={tokens} />
        )}
      </section>
    </main>
  );
}
