import "server-only";
import jwt from "jsonwebtoken";
import { auth } from "@/lib/auth";

const BACKEND_API_URL = process.env.BACKEND_API_URL ?? "http://localhost:8000";
const AUTH_BRIDGE_SECRET = process.env.AUTH_BRIDGE_SECRET;

export class BackendError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "BackendError";
  }
}

/**
 * Mints a short-lived (5 min) HS256 bridge JWT for the currently signed-in
 * user, per docs/CONTRACT.md. Returns null when there is no active session
 * (anonymous browsing) so callers can omit the Authorization header.
 */
async function mintBridgeToken(): Promise<string | null> {
  const session = await auth();
  if (!session?.user?.id) {
    return null;
  }
  if (!AUTH_BRIDGE_SECRET) {
    throw new Error(
      "AUTH_BRIDGE_SECRET is not set. Set it in frontend/.env.local to match backend/.env."
    );
  }

  return jwt.sign(
    { sub: session.user.id, email: session.user.email ?? undefined },
    AUTH_BRIDGE_SECRET,
    { algorithm: "HS256", expiresIn: "5m" }
  );
}

export interface BackendFetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  /** Set to true to require a signed-in session; throws BackendError(401) otherwise. */
  requireAuth?: boolean;
}

/**
 * Server-only fetch helper for talking to the FastAPI backend. Mints the
 * bridge JWT for signed-in users, attaches it as a Bearer token, and omits
 * the header entirely for anonymous requests to public endpoints.
 *
 * Never import this from a Client Component — it is guarded by the
 * "server-only" package and will fail to build if bundled client-side.
 */
export async function backendFetch<T>(
  path: string,
  options: BackendFetchOptions = {}
): Promise<T> {
  const { body, requireAuth, headers, ...rest } = options;

  const token = await mintBridgeToken();

  if (requireAuth && !token) {
    throw new BackendError("Sign in required", 401);
  }

  const finalHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string> | undefined),
  };

  if (token) {
    finalHeaders["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${BACKEND_API_URL}${path}`, {
      ...rest,
      headers: finalHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      // Read-only destination browsing should stay fresh but not hammer
      // the backend on every render; callers can override via `rest`.
      cache: rest.cache ?? "no-store",
    });
  } catch (err) {
    throw new BackendError(
      `Could not reach backend at ${BACKEND_API_URL}: ${
        err instanceof Error ? err.message : String(err)
      }`,
      503
    );
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      if (data?.detail) detail = data.detail;
    } catch {
      // response body wasn't JSON; fall back to statusText
    }
    throw new BackendError(detail || "Backend request failed", response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
