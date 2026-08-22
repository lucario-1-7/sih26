import type { ApiErrorBody, TokenPair } from "@/types/api";
import { clearTokens, getAccessToken, getRefreshToken, setAccessToken } from "@/lib/auth/tokenStore";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  code: string;
  requestId?: string;

  constructor(status: number, body: Partial<ApiErrorBody>) {
    super(body.detail ?? `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.code = body.code ?? "UNKNOWN_ERROR";
    this.requestId = body.request_id;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  query?: Record<string, string | number | undefined | null>;
  /** Skip the Authorization header (e.g. for the OTP endpoints). */
  unauthenticated?: boolean;
  /** Internal — prevents infinite refresh loops. */
  _isRetry?: boolean;
}

function buildUrl(path: string, query?: RequestOptions["query"]): string {
  const url = new URL(BASE_URL.replace(/\/$/, "") + path);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

let refreshPromise: Promise<boolean> | null = null;

/** Attempts a single refresh, de-duplicated across concurrent 401s. */
async function refreshAccessToken(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;
    try {
      const res = await fetch(buildUrl("/auth/refresh"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const pair = (await res.json()) as TokenPair;
      setAccessToken(pair.access_token);
      return true;
    } catch {
      return false;
    }
  })();
  const result = await refreshPromise;
  refreshPromise = null;
  return result;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, query, unauthenticated, _isRetry } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (!unauthenticated) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(buildUrl(path, query), {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && !unauthenticated && !_isRetry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return apiFetch<T>(path, { ...options, _isRetry: true });
    }
    clearTokens();
    throw new ApiError(401, { detail: "Session expired", code: "UNAUTHORIZED" });
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const contentType = res.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await res.json().catch(() => null) : null;

  if (!res.ok) {
    throw new ApiError(res.status, (payload as Partial<ApiErrorBody>) ?? {});
  }

  return payload as T;
}
