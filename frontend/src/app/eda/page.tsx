"use client";

import React, { useEffect, useState } from "react";
import EDAChartPainPoints, {
  PainPointDatum,
} from "@/components/EDAChartPainPoints";
import EDAChartBubble, {
  BubbleDatum,
} from "@/components/EDAChartBubble";
import { backend } from "@/lib/backend";

type AspectRow = {
  aspect: string;
  mentions: number;
  avg_sentiment: number;
};

export default function EDAInsightsPage() {
  const [rows, setRows] = useState<AspectRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setErr(null);
      try {
        const resp = await fetch(backend("/eda/aspects"), {
          method: "GET",
        });

        if (!resp.ok) {
          const text = await resp.text();
          setErr(`Backend ${resp.status}: ${text}`);
          setRows([]);
          setLoading(false);
          return;
        }

        const data = await resp.json();
        const cleaned: AspectRow[] = Array.isArray(data.aspects)
          ? data.aspects.map((item: any) => ({
              aspect: String(item.aspect ?? ""),
              mentions: Number(item.mentions ?? 0),
              avg_sentiment: Number(item.avg_sentiment ?? 0),
            }))
          : [];

        setRows(cleaned);
      } catch (e: any) {
        setErr("Network error talking to backend");
        setRows([]);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  function sentimentColor(v: number) {
    if (v > 0.2)
      return "bg-green-100 text-green-800 border border-green-300";
    if (v < -0.2)
      return "bg-red-100 text-red-800 border border-red-300";
    return "bg-gray-100 text-gray-800 border border-gray-300";
  }

  function sentimentLabel(v: number) {
    if (v > 0.2) return "positive";
    if (v < -0.2) return "negative";
    return "mixed";
  }

  const painPointsData: PainPointDatum[] = rows.map((r) => ({
    aspect: r.aspect,
    avg_sentiment: r.avg_sentiment,
    mentions: r.mentions,
  }));

  const bubbleData: BubbleDatum[] = rows.map((r) => ({
    aspect: r.aspect,
    mentions: r.mentions,
    avg_sentiment: r.avg_sentiment,
  }));

  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-neutral-900 text-center mb-2">
        Aspect Intelligence
      </h1>
      <p className="text-neutral-700 text-center max-w-2xl mx-auto mb-10">
        Live rolling breakdown of what people complain about (or praise),
        aggregated from recent Explain requests.
      </p>

      {loading && (
        <div className="text-neutral-500 text-center text-sm mb-6">
          Loading…
        </div>
      )}

      {err && (
        <div className="text-sm text-red-600 mb-6 whitespace-pre-wrap text-center">
          {err}
        </div>
      )}

      {!loading && !err && rows.length === 0 && (
        <div className="text-neutral-500 text-sm text-center">
          No aspect analytics yet. Hit Explain a few times first.
        </div>
      )}

      {!loading && !err && rows.length > 0 && (
        <>
          <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
            <div className="rounded-xl border border-neutral-200 bg-white shadow-sm p-4 flex flex-col">
              <div className="text-sm font-semibold text-neutral-900 mb-1">
                Top pain points
              </div>
              <div className="text-[11px] text-neutral-500 mb-4">
                More negative sentiment (left / red) = bigger problem.
              </div>
              <div className="flex-1 min-h-[300px]">
                <EDAChartPainPoints data={painPointsData} />
              </div>
            </div>

            <div className="rounded-xl border border-neutral-200 bg-white shadow-sm p-4 flex flex-col">
              <div className="text-sm font-semibold text-neutral-900 mb-1">
                Impact map
              </div>
              <div className="text-[11px] text-neutral-500 mb-4">
                Bubble size = how often it shows up.
              </div>
              <div className="flex-1 min-h-[300px]">
                <EDAChartBubble data={bubbleData} />
              </div>
            </div>
          </section>

          <section className="overflow-hidden rounded-xl border border-neutral-200 shadow-sm bg-white">
            <div className="grid grid-cols-3 bg-neutral-50 text-neutral-600 text-[11px] font-medium uppercase tracking-wide border-b border-neutral-200">
              <div className="px-4 py-3 text-left">Aspect</div>
              <div className="px-4 py-3 text-right">Mentions</div>
              <div className="px-4 py-3 text-right">Avg sentiment</div>
            </div>

            {rows.map((row, idx) => (
              <div
                key={idx}
                className="grid grid-cols-3 items-center text-sm border-b border-neutral-200 last:border-b-0"
              >
                <div className="px-4 py-3 text-neutral-900">
                  <div className="font-medium">{row.aspect}</div>
                </div>

                <div className="px-4 py-3 text-right tabular-nums text-neutral-900">
                  {row.mentions}
                </div>

                <div className="px-4 py-3 text-right">
                  <span
                    className={
                      "inline-block rounded-full px-2 py-1 text-xs font-medium " +
                      sentimentColor(row.avg_sentiment)
                    }
                  >
                    {row.avg_sentiment.toFixed(2)}{" "}
                    {sentimentLabel(row.avg_sentiment)}
                  </span>
                </div>
              </div>
            ))}
          </section>

          <div className="text-[11px] text-neutral-400 text-center mt-6">
            The more red and frequent an aspect is, the more it hurts
            users right now.
          </div>
        </>
      )}
    </main>
  );
}
