import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearTokens, setTokens } from "@/lib/auth/tokenStore";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("apiFetch", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.resetModules();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("attaches the Authorization header when a token is present", async () => {
    setTokens("token-abc", "refresh-abc");
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    const { apiFetch } = await import("@/lib/api/client");
    await apiFetch("/users/me");

    const [, options] = fetchMock.mock.calls[0];
    expect(options.headers.Authorization).toBe("Bearer token-abc");
  });

  it("throws a typed ApiError with status/code/detail on failure", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ detail: "Project not found", code: "NOT_FOUND", request_id: "req-1" }, 404),
    );
    vi.stubGlobal("fetch", fetchMock);

    const { apiFetch, ApiError } = await import("@/lib/api/client");
    await expect(apiFetch("/projects/xyz")).rejects.toMatchObject({
      status: 404,
      code: "NOT_FOUND",
      message: "Project not found",
    });
    await expect(apiFetch("/projects/xyz")).rejects.toBeInstanceOf(ApiError);
  });

  it("refreshes the access token once on 401 and retries the original request", async () => {
    setTokens("stale-token", "refresh-token");
    const fetchMock = vi
      .fn()
      // 1st call: original request fails with 401
      .mockResolvedValueOnce(jsonResponse({ detail: "expired", code: "UNAUTHORIZED" }, 401))
      // 2nd call: refresh endpoint succeeds
      .mockResolvedValueOnce(jsonResponse({ access_token: "new-token", refresh_token: "refresh-token" }, 200))
      // 3rd call: retried original request succeeds
      .mockResolvedValueOnce(jsonResponse({ id: "u1" }, 200));
    vi.stubGlobal("fetch", fetchMock);

    const { apiFetch } = await import("@/lib/api/client");
    const result = await apiFetch("/users/me");

    expect(result).toEqual({ id: "u1" });
    expect(fetchMock).toHaveBeenCalledTimes(3);
    const retryHeaders = fetchMock.mock.calls[2][1].headers;
    expect(retryHeaders.Authorization).toBe("Bearer new-token");
  });

  it("clears the session and throws when refresh itself fails", async () => {
    setTokens("stale-token", "bad-refresh");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "expired", code: "UNAUTHORIZED" }, 401))
      .mockResolvedValueOnce(new Response(null, { status: 401 }));
    vi.stubGlobal("fetch", fetchMock);

    const { apiFetch } = await import("@/lib/api/client");
    const { getAccessToken } = await import("@/lib/auth/tokenStore");

    await expect(apiFetch("/users/me")).rejects.toMatchObject({ status: 401 });
    expect(getAccessToken()).toBeNull();
  });

  it("does not attach Authorization for unauthenticated requests (OTP endpoints)", async () => {
    setTokens("token-abc", "refresh-abc");
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}, 202));
    vi.stubGlobal("fetch", fetchMock);

    const { apiFetch } = await import("@/lib/api/client");
    await apiFetch("/auth/otp/request", { method: "POST", body: { phone: "+911234567890" }, unauthenticated: true });

    const [, options] = fetchMock.mock.calls[0];
    expect(options.headers.Authorization).toBeUndefined();
  });

  it("a 401 from an unauthenticated request (e.g. OTP verify) is thrown directly, never triggers a refresh attempt", async () => {
    // No tokens in storage at all — this is the initial-login case: there is
    // no session to refresh yet.
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ detail: "Invalid or expired OTP", code: "INVALID_OTP" }, 401));
    vi.stubGlobal("fetch", fetchMock);

    const { apiFetch, ApiError } = await import("@/lib/api/client");
    await expect(
      apiFetch("/auth/otp/verify", {
        method: "POST",
        body: { phone: "+911234567890", code: "000000" },
        unauthenticated: true,
      }),
    ).rejects.toMatchObject({ status: 401, code: "INVALID_OTP", message: "Invalid or expired OTP" });

    // Exactly one call — no refresh, no retry attempted for an unauthenticated request.
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await expect(
      apiFetch("/auth/otp/verify", {
        method: "POST",
        body: { phone: "+911234567890", code: "000000" },
        unauthenticated: true,
      }),
    ).rejects.toBeInstanceOf(ApiError);
  });
});
