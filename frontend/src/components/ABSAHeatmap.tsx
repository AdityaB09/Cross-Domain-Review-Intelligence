"use client";

export type AspectItem = {
  aspect: string;
  sentiment: number;      // e.g. -1 to +1
  confidence: number;     // 0-1
  polarity?: string;      // "positive" | "negative" | "neutral" (optional now)
};

export default function ABSAHeatmap({ aspects }: { aspects: AspectItem[] }) {
  if (!aspects || aspects.length === 0) {
    return (
      <p className="text-sm text-neutral-500">
        No aspects to display.
      </p>
    );
  }

  return (
    <div className="flex flex-wrap gap-4">
      {aspects.map((a, idx) => {
        // pick a background color based on sentiment score, fallback if polarity missing
        const sentimentScore = a.sentiment ?? 0;

        // simple scale: red for negative, green for positive, gray for near zero
        let bgClass = "bg-neutral-100 text-neutral-800 border-neutral-300";
        if (sentimentScore > 0.2) {
          bgClass = "bg-green-50 text-green-700 border-green-300";
        } else if (sentimentScore < -0.2) {
          bgClass = "bg-red-50 text-red-700 border-red-300";
        }

        // display label (e.g. "speaker / overheating") plus small bar
        return (
          <div
            key={idx}
            className={`border rounded-md px-3 py-2 min-w-[200px] max-w-[260px] shadow-sm ${bgClass}`}
          >
            <div className="text-sm font-medium">
              {a.aspect}
            </div>

            <div className="mt-1 text-[12px] text-neutral-600 flex flex-col space-y-1">
              <div className="flex justify-between">
                <span>Sentiment</span>
                <span className="font-mono">
                  {sentimentScore.toFixed(2)}
                </span>
              </div>

              <div className="flex justify-between">
                <span>Confidence</span>
                <span className="font-mono">
                  {(a.confidence ?? 0).toFixed(2)}
                </span>
              </div>

              {a.polarity && (
                <div className="flex justify-between">
                  <span>Polarity</span>
                  <span className="font-mono">{a.polarity}</span>
                </div>
              )}
            </div>

            {/* tiny confidence bar */}
            <div className="mt-2 h-1.5 w-full bg-white/50 rounded">
              <div
                className="h-1.5 bg-black/40 rounded"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(0, (a.confidence ?? 0) * 100)
                  )}%`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
