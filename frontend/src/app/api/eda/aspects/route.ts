import { NextResponse } from "next/server";
import { backend } from "@/lib/backend";

export async function GET() {
  try {
    const resp = await fetch(backend("/eda/aspects"), {
      method: "GET",
    });

    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch (err: any) {
    console.error("Proxy /api/eda/aspects → backend /eda/aspects failed:", err);
    return NextResponse.json(
      {
        error: "frontend could not reach backend /eda/aspects",
        detail: String(err),
      },
      { status: 502 }
    );
  }
}
