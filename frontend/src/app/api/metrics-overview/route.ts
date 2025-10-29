import { NextResponse } from "next/server";

const BACKEND = process.env.BACKEND_URL || "https://cdri-backend.onrender.com";

// proxy to backend /model/predict
export async function POST(req: Request) {
  const body = await req.json();

  try {
    const r = await fetch(`${BACKEND}/model/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!r.ok) {
      return NextResponse.json(
        { error: `backend returned ${r.status}` },
        { status: 500 }
      );
    }

    const j = await r.json();
    return NextResponse.json(j);
  } catch (err: any) {
    console.error("predict proxy error:", err);
    return NextResponse.json(
      { error: err.message || "unreachable" },
      { status: 500 }
    );
  }
}
