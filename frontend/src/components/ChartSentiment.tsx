"use client";

import React, { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

// register chart.js pieces once in the client bundle
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// helper: rolling avg smoother
function rollingAvg(values: number[], windowSize = 2): number[] {
  if (values.length === 0) return [];
  const out: number[] = [];
  for (let i = 0; i < values.length; i++) {
    const start = Math.max(0, i - windowSize);
    const end = i + 1;
    const slice = values.slice(start, end);
    const mean =
      slice.reduce((acc, x) => acc + x, 0) / (slice.length || 1);
    out.push(parseFloat(mean.toFixed(2)));
  }
  return out;
}

export default function ChartSentiment({ data }: { data: number[] }) {
  // x-axis labels. You can swap for timestamps if backend eventually returns dates.
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].slice(
    0,
    data.length
  );

  const smooth = useMemo(() => rollingAvg(data, 2), [data]);

  const chartData = {
    labels,
    datasets: [
      // main line (actual daily sentiment)
      {
        label: "Daily sentiment",
        data,
        borderColor: "rgba(17, 24, 39, 1)", // neutral-900
        backgroundColor: (ctx: any) => {
          const { chart } = ctx;
          const { ctx: c } = chart;
          const gradient = c.createLinearGradient(0, 0, 0, 300);
          gradient.addColorStop(0, "rgba(17,24,39,0.18)"); // neutral-900 @ ~18%
          gradient.addColorStop(1, "rgba(17,24,39,0)");
          return gradient;
        },
        fill: true,
        pointRadius: 4,
        pointBackgroundColor: "rgba(17, 24, 39, 1)",
        pointBorderWidth: 0,
        tension: 0.35,
      },
      // smoothed line
      {
        label: "Rolling avg",
        data: smooth,
        borderColor: "rgba(59, 130, 246, 1)", // blue-500
        backgroundColor: "rgba(0,0,0,0)",
        borderDash: [6, 4],
        pointRadius: 0,
        tension: 0.3,
      },
    ],
  };

  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        labels: {
          color: "#4b5563", // neutral-600
          font: { size: 12 },
        },
      },
      tooltip: {
        backgroundColor: "rgba(0,0,0,0.8)",
        titleColor: "#fff",
        bodyColor: "#fff",
        padding: 10,
        displayColors: false,
        callbacks: {
          label: (ctx: any) => {
            const val = ctx.raw;
            return `Sentiment: ${val}`;
          },
        },
      },
    },
    scales: {
      y: {
        min: -1,
        max: 1,
        grid: {
          color: "rgba(156,163,175,0.2)", // neutral-400 @20%
        },
        ticks: {
          color: "#4b5563", // neutral-600
          callback: (v: any) => v.toFixed?.(1) ?? v,
          font: { size: 11 },
        },
        title: {
          display: true,
          text: "Score (-1 to 1)",
          color: "#6b7280", // neutral-500
          font: { size: 11 },
        },
      },
      x: {
        grid: {
          color: "rgba(0,0,0,0)",
        },
        ticks: {
          color: "#4b5563",
          font: { size: 11 },
        },
      },
    },
  };

  return (
    <div className="w-full h-[300px]">
      <Line data={chartData} options={options} />
    </div>
  );
}
