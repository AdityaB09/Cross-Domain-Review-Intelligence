"use client";

import React from "react";

// small pill for each metric
function StatCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex-1 min-w-[200px] rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="text-sm text-neutral-600">{label}</div>
      <div className="text-2xl font-semibold text-neutral-900 mt-1">
        {value}
      </div>
    </div>
  );
}

export default function MetricCards(props: {
  status: string;
  postgres: string;
  redis: string;
  indexReady: string;
}) {
  const { status, postgres, redis, indexReady } = props;

  return (
    <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Status" value={status} />
      <StatCard label="Postgres" value={postgres} />
      <StatCard label="Redis" value={redis} />
      <StatCard label="Index" value={indexReady} />
    </section>
  );
}
