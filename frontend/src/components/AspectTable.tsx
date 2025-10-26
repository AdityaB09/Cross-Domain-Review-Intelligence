"use client";

type Aspect = {
  aspect: string;
  sentiment: string; // "positive" | "negative" | "neutral"
  score: number; // 0..1 confidence-ish
};

export default function AspectTable({ aspects }: { aspects: Aspect[] }) {
  if (!aspects || aspects.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        No aspects detected yet. Paste a review and click Run.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-4">
      {aspects.map((a, i) => (
        <div
          key={i}
          className="rounded-lg border border-gray-200 bg-white shadow-sm p-4 w-60"
        >
          <div className="text-sm font-semibold text-gray-800">
            {a.aspect}
          </div>

          <div className="mt-1 text-xs text-gray-600">
            Sentiment:{" "}
            <span
              className={
                a.sentiment === "negative"
                  ? "text-red-600 font-medium"
                  : a.sentiment === "positive"
                  ? "text-green-600 font-medium"
                  : "text-gray-600 font-medium"
              }
            >
              {a.sentiment}
            </span>
          </div>

          <div className="mt-3">
            <div className="h-2 w-full bg-gray-100 rounded">
              <div
                className={
                  "h-2 rounded " +
                  (a.sentiment === "negative"
                    ? "bg-red-400"
                    : a.sentiment === "positive"
                    ? "bg-green-400"
                    : "bg-gray-400")
                }
                style={{
                  width: `${Math.min(a.score * 100, 100)}%`,
                }}
              />
            </div>
            <div className="text-[10px] text-gray-500 mt-1">
              confidence {Math.round(a.score * 100)}%
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
