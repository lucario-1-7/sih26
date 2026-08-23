"use client";

// Minimal client-side token store. Tokens live in localStorage (this is a
// server-rendered-but-client-authenticated SPA-style dashboard — the backend
// is the security boundary regardless of where the token sits). A tiny
// pub-sub lets the API client and AuthProvider stay in sync without a
// circular import between them.

const ACCESS_KEY = "sociosolve.access_token";
const REFRESH_KEY = "sociosolve.refresh_token";

type Listener = () => void;
const listeners = new Set<Listener>();

function notify() {
  listeners.forEach((l) => l());
}

export function onTokensChanged(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_KEY, accessToken);
  window.localStorage.setItem(REFRESH_KEY, refreshToken);
  notify();
}

export function setAccessToken(accessToken: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_KEY, accessToken);
  notify();
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
  notify();
}
