"use client";

import React from "react";

export default function ReviewCard({
  text,
  score,
}: {
  text: string;
  score: number;
}) {
  // clamp 0..1 for the relevance bar just in case backend gives >1
  const pct = Math.max(0, Math.min(1, score));

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm mb-4">
      {/* header row */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex gap-2 text-xs text-neutral-400 font-mono">
          <span>—</span>
          <span>—</span>
          <span>—</span>
        </div>

        <div className="text-[11px] font-medium text-neutral-600 bg-neutral-100 border border-neutral-300 rounded px-2 py-[2px] leading-none">
          Relevance {(pct * 100).toFixed(0)}%
        </div>
      </div>

      {/* body text */}
      <p className="text-neutral-900 text-base leading-relaxed whitespace-pre-line">
        {text}
      </p>

      {/* bar */}
      <div className="mt-4">
        <div className="text-xs text-neutral-600 mb-1">Relevance</div>
        <div className="h-2 w-full rounded bg-neutral-200 overflow-hidden">
          <div
            className="h-full bg-neutral-800 transition-all"
            style={{ width: `${pct * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
