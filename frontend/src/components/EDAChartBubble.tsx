"use client";

import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export type BubbleDatum = {
  aspect: string;
  mentions: number;
  avg_sentiment: number;
};

function sentimentColor(v: number) {
  if (v > 0.2) return "#86efac"; // green-300
  if (v < -0.2) return "#fca5a5"; // red-300
  return "#e5e7eb"; // gray-200
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-neutral-300 bg-white px-3 py-2 text-[11px] shadow">
      <div className="font-medium text-neutral-900 mb-1">{d.aspect}</div>
      <div className="text-neutral-700">
        Mentions: <span className="font-semibold">{d.mentions}</span>
      </div>
      <div className="text-neutral-700">
        Avg sentiment:{" "}
        <span className="font-semibold">
          {d.avg_sentiment.toFixed(2)}
        </span>
      </div>
    </div>
  );
}

export default function EDAChartBubble({ data }: { data: BubbleDatum[] }) {
  // Transform each row into scatter point with x/y/z
  // x = mentions (how common)
  // y = avg_sentiment (-1..1 how hated/loved)
  // z = bubble size scaler
  const scatterData = data.map((d) => ({
    aspect: d.aspect,
    mentions: d.mentions,
    avg_sentiment: d.avg_sentiment,
    x: d.mentions,
    y: d.avg_sentiment,
    z: Math.max(10, d.mentions * 10),
  }));

  // If there's no data or everything is zero, show a tiny placeholder note
  if (!scatterData.length) {
    return (
      <div className="w-full h-full flex items-center justify-center text-[11px] text-neutral-400">
        No aspect activity yet.
      </div>
    );
  }

  return (
    <div className="w-full h-[320px] sm:h-[360px] md:h-[400px] lg:h-[420px]">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart
          margin={{ top: 20, right: 20, bottom: 40, left: 40 }}
        >
          <XAxis
            dataKey="x"
            name="Mentions"
            tick={{ fontSize: 10, fill: "#525252" }}
            label={{
              value: "Mentions (frequency)",
              position: "bottom",
              offset: 0,
              style: { fontSize: 11, fill: "#525252" },
            }}
          />
          <YAxis
            dataKey="y"
            name="Avg sentiment"
            domain={[-1, 1]}
            tick={{ fontSize: 10, fill: "#525252" }}
            label={{
              value: "Sentiment (-1 angry, +1 happy)",
              angle: -90,
              position: "insideLeft",
              style: { fontSize: 11, fill: "#525252" },
            }}
          />
          <ZAxis dataKey="z" range={[40, 200]} />
          <Tooltip content={<CustomTooltip />} />
          <Scatter
            data={scatterData}
            isAnimationActive={false}
          >
            {scatterData.map((entry, idx) => (
              <Cell
                key={`cell-${idx}`}
                fill={sentimentColor(entry.avg_sentiment)}
                stroke="#525252"
                strokeWidth={0.5}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
