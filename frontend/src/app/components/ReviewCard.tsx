"use client";

export type Review = {
  text: string;
  score?: number; // 0..1 magnitude (optional)
  meta?: { domain?: string; product?: string; date?: string };
};

export default function ReviewCard({ review }: { review: Review }) {
  const { text, score, meta } = review;
  return (
    <div className="rounded-xl border bg-white p-4 shadow-sm">
      <div className="text-sm text-gray-500">
        {meta?.domain ?? "—"} · {meta?.product ?? "—"} · {meta?.date ?? "—"}
      </div>
      <p className="mt-2">{text}</p>
      {typeof score === "number" && (
        <div className="mt-3">
          <div className="text-sm text-gray-500">Relevance</div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full bg-black/70" style={{ width: `${Math.round(score * 100)}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}
