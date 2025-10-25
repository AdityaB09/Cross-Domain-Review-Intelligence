// frontend/src/app/dashboard/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type TrendPoint = {
  day: string;
  avg_sentiment: number;
};

type MetricsOverview = {
  total_reviews: number;
  avg_sentiment: number;
  pct_negative: number;
  top_aspects: string[];
  trend: TrendPoint[];
};

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white px-4 py-4 shadow-sm">
      <div className="text-sm text-gray-600">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-gray-900">{value}</div>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<MetricsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  // fetch metrics from backend via Next route
  useEffect(() => {
    async function go() {
      try {
        const res = await fetch("/api/metrics-overview", {
          method: "GET",
        });
        if (!res.ok) {
          console.error("metrics-overview failed", await res.text());
          setLoading(false);
          return;
        }
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    go();
  }, []);

  // skeleton UI on load
  if (loading) {
    return (
      <div className="px-6 py-8 max-w-7xl mx-auto">
        <h1 className="text-3xl font-semibold text-gray-900">
          Model Overview
        </h1>
        <p className="text-gray-600 mt-2">
          Backend health, index readiness, sentiment drift across recent reviews.
        </p>
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-24 rounded-xl border border-gray-200 bg-gray-100 animate-pulse"
            />
          ))}
        </div>
        <div className="mt-8 h-64 rounded-xl border border-gray-200 bg-gray-100 animate-pulse" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="px-6 py-8 max-w-7xl mx-auto">
        <h1 className="text-3xl font-semibold text-gray-900">
          Model Overview
        </h1>
        <p className="text-gray-600 mt-2">
          No data yet.
        </p>
      </div>
    );
  }

  const {
    total_reviews,
    avg_sentiment,
    pct_negative,
    top_aspects,
    trend,
  } = data;

  return (
    <div className="px-6 py-8 max-w-7xl mx-auto">
      <div className="flex flex-col">
        <h1 className="text-3xl font-semibold text-gray-900">
          Model Overview
        </h1>
        <p className="text-gray-600 mt-2">
          Backend health, index readiness, and sentiment drift across recent
          reviews.
        </p>
      </div>

      {/* metric cards */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Total Reviews"
          value={String(total_reviews)}
        />
        <MetricCard
          label="Avg Sentiment"
          value={avg_sentiment.toFixed(2)}
        />
        <MetricCard
          label="% Negative"
          value={pct_negative.toFixed(1) + "%"}
        />
        <MetricCard
          label="Top Topics"
          value={
            top_aspects.length
              ? top_aspects.join(", ")
              : "—"
          }
        />
      </div>

      {/* sentiment over time chart */}
      <div className="mt-8 rounded-xl border border-gray-200 bg-white shadow-sm p-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Sentiment over time
        </h2>
        <p className="text-gray-600 text-sm mt-1">
          Average sentiment per day (−1 = very negative, +1 = very positive).
        </p>

        <div className="mt-4 w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d1d5db" />
              <XAxis
                dataKey="day"
                stroke="#374151"
                tick={{ fontSize: 12, fill: "#374151" }}
              />
              <YAxis
                domain={[-1, 1]}
                stroke="#374151"
                tick={{ fontSize: 12, fill: "#374151" }}
              />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="avg_sentiment"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
