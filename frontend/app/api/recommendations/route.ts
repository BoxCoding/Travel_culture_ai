import { NextRequest, NextResponse } from "next/server";
import { backendFetch, BackendError } from "@/lib/backend";
import type { RecommendationRequest, RecommendationResponse } from "@/lib/types";

export async function POST(request: NextRequest) {
  let body: RecommendationRequest;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (!Array.isArray(body?.interests)) {
    return NextResponse.json(
      { detail: "interests (string[]) is required" },
      { status: 400 }
    );
  }

  try {
    const data = await backendFetch<RecommendationResponse>(
      "/api/recommendations",
      {
        method: "POST",
        body,
      }
    );
    return NextResponse.json(data);
  } catch (err) {
    const status = err instanceof BackendError ? err.status : 502;
    const detail =
      err instanceof BackendError
        ? err.message
        : "Could not generate recommendations right now.";
    return NextResponse.json({ detail }, { status });
  }
}
