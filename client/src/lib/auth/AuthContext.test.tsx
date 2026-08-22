import { act, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider, useAuth } from "@/lib/auth/AuthContext";
import { clearTokens } from "@/lib/auth/tokenStore";

vi.mock("@/lib/api/auth", () => ({
  getCurrentUser: vi.fn(),
  verifyOtp: vi.fn(),
  logout: vi.fn(),
}));

import { getCurrentUser, logout as apiLogout, verifyOtp } from "@/lib/api/auth";

const UNIVERSITY_USER = {
  id: "u1",
  phone: "+911234567890",
  name: "Dr. Rao",
  role: "coordinator" as const,
  domain: "university" as const,
  organization_id: "org1",
  administrative_area_id: null,
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};

function Probe() {
  const { user, status, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="status">{status}</span>
      <span data-testid="user">{user?.name ?? "none"}</span>
      <button onClick={() => void login("+911234567890", "123456")}>login</button>
      <button onClick={() => void logout()}>logout</button>
    </div>
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    clearTokens();
  });

  it("starts unauthenticated with no stored token", async () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("status").textContent).toBe("unauthenticated"));
    expect(screen.getByTestId("user").textContent).toBe("none");
  });

  it("login stores tokens and loads the user", async () => {
    vi.mocked(verifyOtp).mockResolvedValue({ access_token: "a", refresh_token: "r", token_type: "bearer" });
    vi.mocked(getCurrentUser).mockResolvedValue(UNIVERSITY_USER);

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("status").textContent).toBe("unauthenticated"));

    await act(async () => {
      screen.getByText("login").click();
    });

    await waitFor(() => expect(screen.getByTestId("status").textContent).toBe("authenticated"));
    expect(screen.getByTestId("user").textContent).toBe("Dr. Rao");
  });

  it("logout clears the session even if the server call fails", async () => {
    vi.mocked(verifyOtp).mockResolvedValue({ access_token: "a", refresh_token: "r", token_type: "bearer" });
    vi.mocked(getCurrentUser).mockResolvedValue(UNIVERSITY_USER);
    vi.mocked(apiLogout).mockRejectedValue(new Error("network down"));

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    await act(async () => {
      screen.getByText("login").click();
    });
    await waitFor(() => expect(screen.getByTestId("status").textContent).toBe("authenticated"));

    await act(async () => {
      screen.getByText("logout").click();
    });
    await waitFor(() => expect(screen.getByTestId("status").textContent).toBe("unauthenticated"));
    expect(screen.getByTestId("user").textContent).toBe("none");
  });

  it("session expiry (401 on /users/me) clears tokens and reports unauthenticated", async () => {
    class ApiErrorStub extends Error {
      status = 401;
    }
    vi.mocked(getCurrentUser).mockRejectedValue(new ApiErrorStub("expired"));
    window.localStorage.setItem("sahyog.access_token", "expired-token");
    window.localStorage.setItem("sahyog.refresh_token", "expired-refresh");

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("status").textContent).toBe("unauthenticated"));
  });
});
