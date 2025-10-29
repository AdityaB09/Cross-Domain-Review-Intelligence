import { NextRequest, NextResponse } from "next/server";
import { backend } from "@/lib/backend";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const resp = await fetch(backend("/explain-request"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch (err: any) {
    console.error("Proxy /api/explain-review → backend /explain-request failed:", err);
    return NextResponse.json(
      {
        error: "frontend could not reach backend /explain-request",
        detail: String(err),
      },
      { status: 502 }
    );
  }
}
