import { beforeEach, describe, expect, it, vi } from "vitest";

import { clearTokens, getAccessToken, getRefreshToken, onTokensChanged, setAccessToken, setTokens } from "@/lib/auth/tokenStore";

beforeEach(() => {
  window.localStorage.clear();
});

describe("tokenStore", () => {
  it("starts with no tokens", () => {
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });

  it("setTokens stores both tokens", () => {
    setTokens("access-1", "refresh-1");
    expect(getAccessToken()).toBe("access-1");
    expect(getRefreshToken()).toBe("refresh-1");
  });

  it("setAccessToken updates only the access token", () => {
    setTokens("access-1", "refresh-1");
    setAccessToken("access-2");
    expect(getAccessToken()).toBe("access-2");
    expect(getRefreshToken()).toBe("refresh-1");
  });

  it("clearTokens removes both tokens", () => {
    setTokens("access-1", "refresh-1");
    clearTokens();
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });

  it("notifies listeners on token changes", () => {
    const listener = vi.fn();
    const unsubscribe = onTokensChanged(listener);
    setTokens("access-1", "refresh-1");
    expect(listener).toHaveBeenCalledTimes(1);
    clearTokens();
    expect(listener).toHaveBeenCalledTimes(2);
    unsubscribe();
    setTokens("access-2", "refresh-2");
    expect(listener).toHaveBeenCalledTimes(2);
  });
});
