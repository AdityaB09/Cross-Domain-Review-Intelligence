"use client";

export type AspectItem = {
  aspect: string;
  polarity: "positive" | "negative" | "neutral";
  scores?: { pos?: number; neg?: number; neu?: number };
};

export default function ABSAHeatmap({ aspects }: { aspects: AspectItem[] }) {
  const colors: Record<AspectItem["polarity"], string> = {
    positive: "bg-green-500",
    negative: "bg-red-500",
    neutral: "bg-gray-400",
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {aspects.map((a) => {
        const pct = Math.round(
          (a.scores?.pos ?? a.scores?.neg ?? a.scores?.neu ?? 0.6) * 100
        );
        return (
          <div key={a.aspect} className="rounded-lg border bg-white p-3 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="font-medium">{a.aspect}</div>
              <span className={`text-xs px-2 py-0.5 rounded-full text-white ${colors[a.polarity]}`}>
                {a.polarity}
              </span>
            </div>
            <div className="mt-2 h-2 bg-gray-200 rounded overflow-hidden">
              <div className={`h-full ${colors[a.polarity]}`} style={{ width: `${pct}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
