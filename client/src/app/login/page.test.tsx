import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

vi.mock("@/lib/api/auth", () => ({
  requestOtp: vi.fn(),
  verifyOtp: vi.fn(),
  getCurrentUser: vi.fn(),
  logout: vi.fn(),
}));

import { getCurrentUser, requestOtp, verifyOtp } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { AuthProvider } from "@/lib/auth/AuthContext";
import LoginPage from "@/app/login/page";

const COORDINATOR = {
  id: "u1",
  phone: "+918025741350",
  name: "Coordinator",
  role: "coordinator" as const,
  domain: "university" as const,
  organization_id: "org1",
  administrative_area_id: null,
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};

const CITIZEN = { ...COORDINATOR, role: "citizen" as const, domain: "citizen" as const, organization_id: null };

function renderLogin() {
  return render(
    <AuthProvider>
      <LoginPage />
    </AuthProvider>,
  );
}

async function goToCodeStep() {
  vi.mocked(requestOtp).mockResolvedValue(undefined);
  fireEvent.change(screen.getByLabelText("Phone number"), { target: { value: "+918025741350" } });
  await act(async () => {
    fireEvent.submit(screen.getByText("Send OTP").closest("form")!);
  });
  await waitFor(() => expect(screen.getByLabelText("One-time code")).toBeInTheDocument());
}

async function submitCode(code: string) {
  fireEvent.change(screen.getByLabelText("One-time code"), { target: { value: code } });
  await act(async () => {
    fireEvent.submit(screen.getByText("Verify & sign in").closest("form")!);
  });
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it("shows the backend's real error for an invalid OTP, not 'session has expired'", async () => {
    renderLogin();
    await goToCodeStep();

    vi.mocked(verifyOtp).mockRejectedValue(new ApiError(401, { detail: "Invalid or expired OTP", code: "INVALID_OTP" }));

    await submitCode("000000");

    await waitFor(() => expect(screen.getByText("Invalid or expired OTP")).toBeInTheDocument());
    expect(screen.queryByText(/session has expired/i)).not.toBeInTheDocument();
  });

  it("redirects a university coordinator to /organization, not by hardcoded phone", async () => {
    renderLogin();
    await goToCodeStep();

    vi.mocked(verifyOtp).mockResolvedValue({ access_token: "a", refresh_token: "r", token_type: "bearer" });
    vi.mocked(getCurrentUser).mockResolvedValue(COORDINATOR);

    await submitCode("123456");

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/organization"));
  });

  it("redirects a citizen to /citizen, driven by the actual /users/me response", async () => {
    renderLogin();
    await goToCodeStep();

    vi.mocked(verifyOtp).mockResolvedValue({ access_token: "a", refresh_token: "r", token_type: "bearer" });
    vi.mocked(getCurrentUser).mockResolvedValue(CITIZEN);

    await submitCode("123456");

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/citizen"));
  });
});
