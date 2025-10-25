// frontend/src/app/explain/page.tsx
"use client";

import React, { useState } from "react";
import TokenAttributionRow, { TokenChip } from "@/components/TokenAttributionRow";

type AspectItem = {
  aspect: string;
  sentiment: string;
  score: number;
};

// NOTE: we assume you already have an API route /api/predict wrapping backend /model/predict
// and /api/explain wrapping backend /explain. If names differ in your project,
// just update the fetch URLs below.

export default function ExplainPage() {
  const [text, setText] = useState(
    "The camera is insanely sharp and I love it, but the phone overheats and the speaker buzzes"
  );

  const [loading, setLoading] = useState(false);

  const [aspects, setAspects] = useState<AspectItem[]>([]);
  const [tokens, setTokens] = useState<TokenChip[]>([]);

  async function handleRun() {
    setLoading(true);
    try {
      // 1. get aspect-level sentiment
      const predRes = await fetch("/api/predict", {
        method: "POST",
        body: JSON.stringify({ text }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      // 2. get token attributions
      const expRes = await fetch("/api/explain", {
        method: "POST",
        body: JSON.stringify({ text }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (predRes.ok) {
        const predJson = await predRes.json();
        // expected:
        // {
        //   sentiment: "positive",
        //   score: 0.9,
        //   aspects: [
        //     { aspect: "battery life", sentiment: "positive", score: 0.95},
        //     ...
        //   ]
        // }
        setAspects(predJson.aspects || []);
      } else {
        console.error("predict failed", await predRes.text());
        setAspects([]);
      }

      if (expRes.ok) {
        const expJson = await expRes.json();
        // expected:
        // {
        //   text: "....",
        //   tokens: [
        //      {token: "camera", attribution: 0.9},
        //      {token: "overheats", attribution: -0.9},
        //   ]
        // }
        setTokens(expJson.tokens || []);
      } else {
        console.error("explain failed", await expRes.text());
        setTokens([]);
      }
    } catch (err) {
      console.error(err);
      setAspects([]);
      setTokens([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="px-6 py-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-semibold text-gray-900 text-center">
        Explainability &amp; ABSA
      </h1>
      <p className="text-gray-600 text-center mt-3 max-w-2xl mx-auto">
        Extract aspects (battery, charging, camera...) and see sentiment per aspect.
        Then inspect which specific words pushed the model positive or negative.
      </p>

      {/* input box */}
      <div className="mt-8">
        <textarea
          className="w-full rounded-md border border-gray-300 bg-white p-4 text-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black min-h-[120px]"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </div>

      <div className="mt-4">
        <button
          onClick={handleRun}
          disabled={loading}
          className="bg-black text-white rounded-md px-4 py-2 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:bg-gray-800"
        >
          {loading ? "Running..." : "Run"}
        </button>
      </div>

      {/* Aspect Heatmap / ABSA */}
      <section className="mt-8 rounded-xl border border-gray-200 bg-white shadow-sm p-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Aspect Heatmap
        </h2>
        <p className="text-gray-600 text-sm mt-1">
          Aspect-level sentiment (e.g. charging port negative, camera positive).
        </p>

        <div className="mt-4 flex flex-wrap gap-4">
          {aspects.length === 0 ? (
            <div className="text-sm text-gray-500">
              Run analysis to see aspect-level sentiment.
            </div>
          ) : (
            aspects.map((a, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-gray-300 bg-white px-3 py-2 shadow-sm w-full sm:w-auto"
              >
                <div className="text-sm font-semibold text-gray-900">
                  {a.aspect}
                </div>
                <div className="text-xs text-gray-600 flex items-center gap-2 mt-1">
                  <span>
                    {a.sentiment} ({a.score?.toFixed
                      ? a.score.toFixed(2)
                      : a.score}
                    )
                  </span>
                  <div className="h-2 w-28 rounded bg-gray-100 overflow-hidden border border-gray-200">
                    {/* little sentiment bar */}
                    <div
                      className={
                        "h-full " +
                        (a.sentiment === "negative"
                          ? "bg-red-400"
                          : a.sentiment === "positive"
                          ? "bg-green-500"
                          : "bg-gray-400")
                      }
                      style={{
                        width: `${
                          a.score && a.score > 1
                            ? 100
                            : a.score && a.score < 0
                            ? 10
                            : Math.round((a.score || 0.1) * 100)
                        }%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Token attributions */}
      <section className="mt-6 rounded-xl border border-gray-200 bg-white shadow-sm p-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Token attributions
        </h2>
        <p className="text-gray-600 text-sm mt-1">
          Words that most influenced the model.
        </p>

        <div className="mt-4">
          <TokenAttributionRow tokens={tokens} />
        </div>
      </section>
    </div>
  );
}
