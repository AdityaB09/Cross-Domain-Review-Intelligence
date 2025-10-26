"use client";

import React, { useEffect, useState } from "react";

// adjust these imports if your folder layout differs
import MetricCards from "@/components/MetricCards";
import ChartSentiment from "@/components/ChartSentiment";

type MetricsResponse = {
  status: string;
  postgres: string;
  redis: string;
  index: string;
  trend: number[];
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<MetricsResponse>({
    status: "ok",
    postgres: "ok",
    redis: "ok",
    index: "ready",
    trend: [-0.2, 0.05, 0.3, -0.1, 0.6], // fallback sparkline
  });

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const resp = await fetch("/api/metrics-overview", {
          method: "GET",
          cache: "no-store",
        });

        if (!resp.ok) {
          setError(
            `Couldn't load latest metrics (metrics api ${resp.status}).`
          );
          return;
        }

        const data = await resp.json();
        setMetrics((old) => ({
          ...old,
          ...data,
          trend:
            Array.isArray(data.trend) && data.trend.length
              ? data.trend
              : old.trend,
        }));
      } catch (err: any) {
        console.error("metrics fetch failed", err);
        setError("Couldn't load latest metrics (network).");
      }
    }

    load();
  }, []);

  // compute direction for badge
  const t = metrics.trend;
  const delta = t[t.length - 1] - t[0];
  const improving = delta >= 0;

  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-neutral-900 mb-2">
        Model Overview
      </h1>
      <p className="text-neutral-700 mb-4">
        Backend health, index readiness, and sentiment drift across recent
        reviews.
      </p>

      {/* Helpful but not doomsday: only show in dev */}
      {error && process.env.NODE_ENV !== "production" && (
        <p className="text-sm text-red-600 mb-4">
          {error} Showing fallback dummy values.
        </p>
      )}

      {/* four metric tiles */}
      <MetricCards
        status={metrics.status}
        postgres={metrics.postgres}
        redis={metrics.redis}
        indexReady={metrics.index}
      />

      {/* sentiment section */}
      <section className="mt-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-4">
          <div>
            <h2 className="text-lg font-semibold text-neutral-800 flex items-center gap-2">
              Sentiment over time
            </h2>
            <p className="text-sm text-neutral-500 max-w-xl">
              Rolling sentiment score of recent indexed reviews. 1 = very
              positive, -1 = very negative.
            </p>
          </div>

          <div
            className={`text-sm font-medium px-2 py-1 rounded-md border self-start ${
              improving
                ? "bg-green-50 text-green-700 border-green-300"
                : "bg-red-50 text-red-700 border-red-300"
            }`}
          >
            {improving
              ? "↗ sentiment improving"
              : "↘ sentiment worsening"}
          </div>
        </div>

        <ChartSentiment data={metrics.trend} />
      </section>
    </main>
  );
}
