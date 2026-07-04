import { NextRequest, NextResponse } from "next/server";
import { backendFetch, BackendError } from "@/lib/backend";
import type { ChatRequest, ChatResponse } from "@/lib/types";

export async function POST(request: NextRequest) {
  let body: ChatRequest;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (!body?.message) {
    return NextResponse.json({ detail: "message is required" }, { status: 400 });
  }

  try {
    const data = await backendFetch<ChatResponse>("/api/chat", {
      method: "POST",
      body,
      requireAuth: true,
    });
    return NextResponse.json(data);
  } catch (err) {
    const status = err instanceof BackendError ? err.status : 502;
    const detail =
      err instanceof BackendError
        ? err.message
        : "The concierge is unavailable right now.";
    return NextResponse.json({ detail }, { status });
  }
}
