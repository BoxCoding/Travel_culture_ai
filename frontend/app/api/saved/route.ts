import { NextRequest, NextResponse } from "next/server";
import { backendFetch, BackendError } from "@/lib/backend";
import type { SavedItem } from "@/lib/types";

export async function GET() {
  try {
    const data = await backendFetch<SavedItem[]>("/api/me/saved", {
      requireAuth: true,
    });
    return NextResponse.json(data);
  } catch (err) {
    const status = err instanceof BackendError ? err.status : 502;
    const detail =
      err instanceof BackendError
        ? err.message
        : "Could not load saved experiences right now.";
    return NextResponse.json({ detail }, { status });
  }
}

export async function POST(request: NextRequest) {
  let body: { id?: string; destination_id?: string; item_type?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (!body?.id || !body?.destination_id || !body?.item_type) {
    return NextResponse.json(
      { detail: "id, destination_id, and item_type are required" },
      { status: 400 }
    );
  }

  try {
    const data = await backendFetch(`/api/experiences/${body.id}/save`, {
      method: "POST",
      requireAuth: true,
      body: {
        item_type: body.item_type,
        destination_id: body.destination_id,
      },
    });
    return NextResponse.json(data ?? { ok: true });
  } catch (err) {
    const status = err instanceof BackendError ? err.status : 502;
    const detail =
      err instanceof BackendError
        ? err.message
        : "Could not save this experience right now.";
    return NextResponse.json({ detail }, { status });
  }
}
