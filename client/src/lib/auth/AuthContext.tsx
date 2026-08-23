"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { demoLogin as apiDemoLogin, getCurrentUser, logout as apiLogout, verifyOtp as apiVerifyOtp } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { clearTokens, getAccessToken, getRefreshToken, onTokensChanged, setTokens } from "@/lib/auth/tokenStore";
import type { UserResponse } from "@/types/api";

interface AuthState {
  user: UserResponse | null;
  status: "loading" | "authenticated" | "unauthenticated";
  login: (phone: string, code: string) => Promise<UserResponse>;
  /** PRESENTATION-ONLY — see lib/api/auth.ts demoLogin. */
  loginDemo: (persona: string) => Promise<UserResponse>;
  logout: () => Promise<void>;
  refetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [status, setStatus] = useState<AuthState["status"]>("loading");

  const loadUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      setStatus("unauthenticated");
      return;
    }
    try {
      const me = await getCurrentUser();
      setUser(me);
      setStatus("authenticated");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearTokens();
      }
      setUser(null);
      setStatus("unauthenticated");
    }
  }, []);

  useEffect(() => {
    void loadUser();
    // Re-check whenever tokens change anywhere in the app (login/logout/refresh-failure).
    return onTokensChanged(() => {
      if (!getAccessToken()) {
        setUser(null);
        setStatus("unauthenticated");
      }
    });
  }, [loadUser]);

  const login = useCallback(async (phone: string, code: string) => {
    const pair = await apiVerifyOtp(phone, code);
    setTokens(pair.access_token, pair.refresh_token);
    const me = await getCurrentUser();
    setUser(me);
    setStatus("authenticated");
    return me;
  }, []);

  const loginDemo = useCallback(async (persona: string) => {
    const pair = await apiDemoLogin(persona);
    setTokens(pair.access_token, pair.refresh_token);
    const me = await getCurrentUser();
    setUser(me);
    setStatus("authenticated");
    return me;
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken) await apiLogout(refreshToken);
    } catch {
      // Best-effort — clear local session regardless.
    }
    clearTokens();
    setUser(null);
    setStatus("unauthenticated");
  }, []);

  return (
    <AuthContext.Provider value={{ user, status, login, loginDemo, logout, refetchUser: loadUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
