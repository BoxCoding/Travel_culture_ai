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
  let body: { id?: number | string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (body?.id === undefined || body?.id === null) {
    return NextResponse.json({ detail: "id is required" }, { status: 400 });
  }

  try {
    const data = await backendFetch(`/api/experiences/${body.id}/save`, {
      method: "POST",
      requireAuth: true,
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
