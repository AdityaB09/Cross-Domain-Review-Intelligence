// frontend/src/app/dashboard/page.tsx
"use client";
import { useEffect, useState } from "react";

type Metrics = {
  total_reviews: number;
  total_domains: number;
  last_ingested_at?: string | null;
};

export default function DashboardPage() {
  const [data, setData] = useState<Metrics | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/metrics-overview", { cache: "no-store" });
        if (!r.ok) throw new Error(await r.text());
        setData(await r.json());
      } catch (e: any) {
        setErr(e.message ?? "Failed to load metrics");
      }
    })();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      {err && <div className="text-sm text-red-600">{err}</div>}
      {data && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="rounded-lg border p-4 bg-white">
            <div className="text-sm text-neutral-500">Total reviews</div>
            <div className="text-2xl font-semibold">{data.total_reviews}</div>
          </div>
          <div className="rounded-lg border p-4 bg-white">
            <div className="text-sm text-neutral-500">Domains</div>
            <div className="text-2xl font-semibold">{data.total_domains}</div>
          </div>
          <div className="rounded-lg border p-4 bg-white">
            <div className="text-sm text-neutral-500">Last ingested</div>
            <div className="text-sm">{data.last_ingested_at ?? "—"}</div>
          </div>
        </div>
      )}
    </div>
  );
}
