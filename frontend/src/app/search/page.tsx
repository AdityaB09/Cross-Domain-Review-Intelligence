"use client";

import React, { useState } from "react";
import ReviewCard from "@/components/ReviewCard";

type Hit = {
  text: string;
  score: number;
};

export default function SearchPage() {
  const [query, setQuery] = useState(
    "The camera is insanely sharp, but the phone overheats and the speaker buzzes"
  );

  const [results, setResults] = useState<Hit[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // small helper to dedupe identical texts
  function uniqueByText(hits: Hit[]): Hit[] {
    const seen = new Set<string>();
    const out: Hit[] = [];
    for (const h of hits) {
      const norm = h.text.trim();
      if (!seen.has(norm)) {
        seen.add(norm);
        out.push(h);
      }
    }
    return out;
  }

  async function runSearch() {
    setLoading(true);
    setErr(null);

    try {
      const resp = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!resp.ok) {
        // backend might 404/405 in docker until you wire /search
        // so show a reasonable fallback
        setErr(
          `Search API ${resp.status}. Showing demo matches instead.`
        );

        const demo: Hit[] = [
          {
            text:
              "Camera is sharp but the charging is slow",
            score: 0.92,
          },
          {
            text:
              "Terrible speaker and overheating after 10 minutes",
            score: 0.74,
          },
          {
            text:
              "Camera is sharp but the charging is slow", // dup on purpose
            score: 0.90,
          },
        ];

        setResults(uniqueByText(demo));
        setLoading(false);
        return;
      }

      const data = await resp.json();

      // expect backend to give { hits: [{text, score}, ...] }
      const cleaned = uniqueByText(
        Array.isArray(data.hits)
          ? data.hits.map((h: any) => ({
              text: String(h.text ?? ""),
              score: Number(h.score ?? 0),
            }))
          : []
      );

      setResults(cleaned);
    } catch (e: any) {
      console.error("search failed", e);
      setErr("Network error. Showing demo matches.");

      const demo: Hit[] = [
        {
          text:
            "Camera is sharp but the charging is slow",
          score: 0.92,
        },
        {
          text:
            "Terrible speaker and overheating after 10 minutes",
          score: 0.74,
        },
        {
          text:
            "Camera is sharp but the charging is slow", // dup on purpose
          score: 0.90,
        },
      ];

      setResults(uniqueByText(demo));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-neutral-900 text-center mb-2">
        Semantic Search
      </h1>
      <p className="text-neutral-700 text-center max-w-2xl mx-auto mb-8">
        Describe an experience or complaint. We’ll find similar real
        reviews. (Make sure you’ve ingested data and run /build.)
      </p>

      {/* query input row */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-8">
        <input
          className="flex-1 rounded border border-neutral-300 bg-white px-4 py-3 text-neutral-900 placeholder-neutral-500 shadow-sm focus:outline-none focus:ring-2 focus:ring-black/80 focus:border-black/80"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="speaker crackles at high volume..."
        />
        <button
          onClick={runSearch}
          disabled={loading}
          className="bg-black text-white text-base font-medium rounded px-5 py-3 shadow-sm hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {err && (
        <div className="text-sm text-red-600 mb-4">{err}</div>
      )}

      {/* results list */}
      <section>
        {results.length === 0 && !loading && (
          <div className="text-neutral-500 text-sm">
            No results yet.
          </div>
        )}

        {results.map((hit, idx) => (
          <ReviewCard
            key={idx}
            text={hit.text}
            score={hit.score}
          />
        ))}
      </section>
    </main>
  );
}
