import { apiFetch } from "@/lib/api/client";
import type { TokenPair, UserResponse } from "@/types/api";

export function requestOtp(phone: string): Promise<void> {
  return apiFetch<void>("/auth/otp/request", {
    method: "POST",
    body: { phone },
    unauthenticated: true,
  });
}

export function verifyOtp(phone: string, code: string): Promise<TokenPair> {
  return apiFetch<TokenPair>("/auth/otp/verify", {
    method: "POST",
    body: { phone, code },
    unauthenticated: true,
  });
}

/**
 * PRESENTATION-ONLY. Bypasses the OTP challenge entirely — issues a real
 * session for a real, backend-persisted demo user with the given
 * organizational persona. Only ever called from a UI path gated by
 * NEXT_PUBLIC_DEMO_MODE, and only ever succeeds if the backend's own
 * DEMO_MODE is also explicitly enabled (404 otherwise) — this flag alone
 * can never grant access.
 */
export function demoLogin(persona: string): Promise<TokenPair> {
  return apiFetch<TokenPair>("/auth/demo/login", {
    method: "POST",
    body: { persona },
    unauthenticated: true,
  });
}

export function refreshTokens(refresh_token: string): Promise<TokenPair> {
  return apiFetch<TokenPair>("/auth/refresh", {
    method: "POST",
    body: { refresh_token },
    unauthenticated: true,
  });
}

export function logout(refresh_token: string): Promise<void> {
  return apiFetch<void>("/auth/logout", { method: "POST", body: { refresh_token } });
}

export function getCurrentUser(): Promise<UserResponse> {
  return apiFetch<UserResponse>("/users/me");
}
