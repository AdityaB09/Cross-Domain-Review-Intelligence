"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export type PainPointDatum = {
  aspect: string;
  avg_sentiment: number; // -1..1
  mentions: number;
};

// helper: color based on sentiment
function sentimentColor(v: number) {
  if (v > 0.2) return "#86efac"; // green-300
  if (v < -0.2) return "#fca5a5"; // red-300
  return "#e5e7eb"; // gray-200
}

// custom tooltip
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-neutral-300 bg-white px-3 py-2 text-[11px] shadow">
      <div className="font-medium text-neutral-900 mb-1">{d.aspect}</div>
      <div className="text-neutral-700">
        Sentiment:{" "}
        <span className="font-semibold">
          {d.avg_sentiment.toFixed(2)}
        </span>
      </div>
      <div className="text-neutral-700">
        Mentions: <span className="font-semibold">{d.mentions}</span>
      </div>
    </div>
  );
}

export default function EDAChartPainPoints({
  data,
}: {
  data: PainPointDatum[];
}) {
  // We'll plot NEGATIVE first, so sort ascending by avg_sentiment
  // (most negative = top)
  const sorted = [...data].sort(
    (a, b) => a.avg_sentiment - b.avg_sentiment
  );

  // recharts wants height. We'll make dynamic height based on rows
  const chartHeight = Math.max(200, sorted.length * 32 + 40);

  return (
    <div className="w-full h-[400px] sm:h-[480px] md:h-[520px] lg:h-[560px] xl:h-[600px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 20, right: 20, bottom: 20, left: 80 }}
        >
          <XAxis
            type="number"
            domain={[-1, 1]}
            tick={{ fontSize: 10, fill: "#525252" }}
          />
          <YAxis
            type="category"
            dataKey="aspect"
            width={120}
            tick={{ fontSize: 10, fill: "#171717" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="avg_sentiment"
            radius={[4, 4, 4, 4]}
            isAnimationActive={false}
          >
            {sorted.map((entry, idx) => (
              <Cell
                key={`cell-${idx}`}
                fill={sentimentColor(entry.avg_sentiment)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
