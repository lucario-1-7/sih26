import { apiClient } from './client';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: string;
  phone: string;
  name: string;
  role: string;
}

const ACCESS_TOKEN_KEY = 'sociosolve_access_token';
const REFRESH_TOKEN_KEY = 'sociosolve_refresh_token';

export const authApi = {
  /**
   * Exchanges a real MSG91 OTP Widget access-token (already verified
   * client-side by MSG91 itself) for a Sahyog session. The backend
   * independently re-verifies the token with MSG91 server-side before
   * issuing anything — this call genuinely fails if that verification
   * fails, it never falls back to a fabricated session.
   */
  async verifyMsg91AccessToken(accessToken: string): Promise<AuthTokens> {
    const res = await apiClient<AuthTokens>('/auth/customer/msg91/verify', {
      method: 'POST',
      body: JSON.stringify({ access_token: accessToken }),
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem(ACCESS_TOKEN_KEY, res.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, res.refresh_token);
    }
    return res;
  },

  async getCurrentUser(): Promise<CurrentUser> {
    return apiClient<CurrentUser>('/users/me');
  },

  /**
   * PRESENTATION-ONLY. Bypasses the OTP challenge entirely — issues a real
   * Sahyog session for a real, backend-persisted demo citizen. Only ever
   * called from a UI path gated by NEXT_PUBLIC_DEMO_MODE, and only ever
   * succeeds if the backend's own DEMO_MODE is also explicitly enabled
   * (404 otherwise) — this flag alone can never grant access.
   */
  async demoLogin(persona: string = 'citizen'): Promise<AuthTokens> {
    const res = await apiClient<AuthTokens>('/auth/demo/login', {
      method: 'POST',
      body: JSON.stringify({ persona }),
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem(ACCESS_TOKEN_KEY, res.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, res.refresh_token);
    }
    return res;
  },

  hasSession(): boolean {
    if (typeof window === 'undefined') return false;
    return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
  },

  /**
   * Logout and clear local tokens. A failed server-side revocation still
   * clears the local session — the device must never be left looking
   * logged-in — but it is not silently treated as a success the caller
   * can't distinguish from a real one; callers that care can inspect the
   * rejected promise.
   */
  async logout(): Promise<void> {
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;

    if (typeof window !== 'undefined') {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }

    if (refreshToken) {
      await apiClient('/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
  },
};
