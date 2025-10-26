"use client";

export default function TokenAttributionsPills({
  tokens,
}: {
  tokens: { token: string; score: number }[];
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {tokens.map((t, idx) => {
        const positive = t.score > 0;
        const bg = positive
          ? "bg-green-50 text-green-700 border-green-300"
          : "bg-red-50 text-red-700 border-red-300";

        return (
          <span
            key={idx}
            className={`inline-flex items-center border rounded-md px-2 py-1 text-sm ${bg}`}
          >
            <span className="font-medium mr-1">{t.token}</span>
            <span className="text-xs opacity-70">
              {t.score.toFixed(2)}
            </span>
          </span>
        );
      })}
    </div>
  );
}
