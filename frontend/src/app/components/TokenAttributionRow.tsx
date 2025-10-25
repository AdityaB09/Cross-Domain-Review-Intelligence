// frontend/src/components/TokenAttributionRow.tsx
"use client";

import React from "react";

export type TokenChip = {
  token: string;
  attribution: number;
};

function hueForAttribution(attr: number): string {
  // attr > 0 => blue/green-ish
  // attr < 0 => red-ish
  // We'll do a soft background alpha.
  if (attr > 0.2) {
    return "bg-green-100 text-green-800 border-green-300";
  }
  if (attr < -0.2) {
    return "bg-red-100 text-red-800 border-red-300";
  }
  return "bg-gray-100 text-gray-700 border-gray-300";
}

export default function TokenAttributionRow({ tokens }: { tokens: TokenChip[] }) {
  if (!tokens || tokens.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        Run analysis to highlight which words drove the model.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {tokens.map((t, i) => (
        <div
          key={i}
          className={
            "rounded-lg border px-2 py-1 text-sm font-medium " +
            hueForAttribution(t.attribution)
          }
          title={`attribution: ${t.attribution.toFixed(2)}`}
        >
          {t.token}
        </div>
      ))}
    </div>
  );
}
