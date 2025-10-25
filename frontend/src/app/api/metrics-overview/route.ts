// frontend/src/app/api/metrics-overview/route.ts

import { NextRequest, NextResponse } from "next/server";

// BACKEND URL inside docker compose network is `http://backend:8080`.
// But when you're hitting from the browser via Next server route,
// this code runs on the server side of the Next container so it CAN reach backend by service name.
const BACKEND = process.env.BACKEND_ORIGIN || "http://backend:8080";

export async function GET(req: NextRequest) {
  const url = `${BACKEND}/metrics/overview`;

  try {
    const r = await fetch(url, {
      method: "GET",
    });
    const text = await r.text();

    if (!r.ok) {
      return NextResponse.json(
        { error: `Backend error: ${text}` },
        { status: r.status },
      );
    }

    return new NextResponse(text, {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message || "fetch failed" },
      { status: 500 },
    );
  }
}
