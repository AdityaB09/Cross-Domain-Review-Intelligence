import { BACKEND_URL } from "@/lib/config";

export const dynamic = "force-dynamic";

export async function GET() {
  const r = await fetch(`${BACKEND_URL}/metrics-overview`, { cache: "no-store" });
  const data = await r.json();
  return new Response(JSON.stringify(data), { headers: { "Content-Type": "application/json" } });
}
