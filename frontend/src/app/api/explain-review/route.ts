// frontend/src/app/api/explain-request/route.ts
import { NextRequest, NextResponse } from "next/server";

// point this to your backend container name and route
// backend already handled token highlighting + aspects under /model/predict and /explain
// From your earlier logs, /model/predict works (200 OK) and /explain was 404 unless you added that router.
// We'll make a unified "analyze" call here that hits both /model/predict and /explain (if available)
// and falls back gracefully.

const BACKEND_BASE = "http://backend:8080";

export async function POST(req: NextRequest) {
  try {
    const { text } = await req.json();

    // 1. Sentiment + token attribution from /model/predict (this worked: 200 OK in your logs)
    const predResp = await fetch(`${BACKEND_BASE}/model/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!predResp.ok) {
      // hard fail only if even /model/predict is broken
      return NextResponse.json(
        { error: "predict failed", status: predResp.status },
        { status: 502 },
      );
    }

    const predJson = await predResp.json();
    // Let's assume predJson looks like:
    // {
    //   tokens: [{ token: "pain", score: -0.9 }, ...],
    //   sentiment: "negative" | "positive"
    // }

    const tokens = predJson.tokens ?? [];

    // 2. Aspect-level sentiment from /explain (your backend 404s this right now)
    // We'll try it, but if it's 404 we'll just return [].
    let aspects: any[] = [];

    try {
      const explResp = await fetch(`${BACKEND_BASE}/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (explResp.ok) {
        const explJson = await explResp.json();
        // expect explJson.aspects maybe:
        // [
        //   { aspect: "the speaker", sentiment: -0.7, confidence: 0.8 }
        // ]
        aspects = explJson.aspects ?? [];
      } else {
        // backend said 404 (not implemented) -> fine, empty aspects
        aspects = [];
      }
    } catch (err) {
      // backend container doesn't even have /explain route -> fine, empty
      aspects = [];
    }

    // Now return one unified payload as the frontend expects
    return NextResponse.json(
      {
        aspects,
        tokens,
      },
      { status: 200 },
    );
  } catch (err: any) {
    console.error("Explain proxy error", err);
    return NextResponse.json(
      { error: "unhandled on server", detail: String(err) },
      { status: 500 },
    );
  }
}
