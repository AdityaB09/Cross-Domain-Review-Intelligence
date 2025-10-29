import { BACKEND_URL } from "@/lib/config";

export async function POST(req: Request) {
  const payload = await req.json();
  const r = await fetch(`${BACKEND_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await r.json();
  return new Response(JSON.stringify(data), { headers: { "Content-Type": "application/json" } });
}
