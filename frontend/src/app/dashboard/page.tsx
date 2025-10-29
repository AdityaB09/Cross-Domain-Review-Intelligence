import React from "react";
import MetricCards from "@/components/MetricCards";
import ChartSentiment from "@/components/ChartSentiment";
import { safeJsonFetch } from "@/lib/backend";

type MetricsResp = {
  status: string;
  redis: string;
  postgres: string;
  index: string;
  sentiment_over_time: { day: string; score: number; rolling: number }[];
} | null;

export default async function DashboardPage() {
  // safe fetch so build won't die
  const metrics: MetricsResp = await safeJsonFetch<MetricsResp>("/metrics");

  const sentimentSeries = metrics?.sentiment_over_time || [];

  return (
    <main className="max-w-6xl mx-auto px-4 py-10 space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-neutral-900">
          Model Overview
        </h1>
        <p className="text-neutral-600">
          Backend health, index readiness, and sentiment drift across
          recent reviews.
        </p>
      </section>

      <MetricCards
        status={metrics?.status ?? "unknown"}
        redis={metrics?.redis ?? "unknown"}
        postgres={metrics?.postgres ?? "unknown"}
        index={metrics?.index ?? "unknown"}
      />

      <ChartSentiment data={sentimentSeries} />
    </main>
  );
}
