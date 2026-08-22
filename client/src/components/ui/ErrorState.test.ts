import { describe, expect, it } from "vitest";

import { authErrorMessage, errorMessage } from "@/components/ui/ErrorState";
import { ApiError } from "@/lib/api/client";

describe("errorMessage (protected/session-context requests)", () => {
  it("maps a 401 to the generic session-expired message", () => {
    const err = new ApiError(401, { detail: "Session expired", code: "UNAUTHORIZED" });
    expect(errorMessage(err)).toBe("Your session has expired. Please sign in again.");
  });
});

describe("authErrorMessage (initial login flow — OTP request/verify)", () => {
  it("shows the backend's actual detail for an invalid/expired OTP, not the generic session-expired copy", () => {
    const err = new ApiError(401, { detail: "Invalid or expired OTP", code: "INVALID_OTP" });
    expect(authErrorMessage(err)).toBe("Invalid or expired OTP");
    expect(authErrorMessage(err)).not.toMatch(/session has expired/i);
  });

  it("falls back to a generic (non-session-expired) message for a non-ApiError failure", () => {
    expect(authErrorMessage(new Error("network down"))).not.toMatch(/session has expired/i);
  });

  it("still surfaces validation errors distinctly from OTP errors", () => {
    const err = new ApiError(422, { detail: "Validation failed", code: "VALIDATION_ERROR" });
    expect(authErrorMessage(err)).toBe("Validation failed");
  });
});
