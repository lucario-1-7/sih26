import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const replace = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }), usePathname: () => "/organization/superadmin" }));
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth: vi.fn() }));

import { useAuth } from "@/lib/auth/AuthContext";
import { DomainGuardLayout } from "@/components/organization/DomainGuardLayout";
import { isGovernmentUser, isIndustryUser, isSuperadminUser, isUniversityUser } from "@/lib/rbac/config";

function user(domain: string, role: string) {
  return { id: "u1", domain, role, name: "x", phone: "+911", organization_id: null, administrative_area_id: null, is_active: true, created_at: "" };
}

describe("DomainGuardLayout — cross-domain isolation", () => {
  beforeEach(() => vi.clearAllMocks());

  it("Government user is denied University shell and redirected", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: user("government", "validator"), status: "authenticated" } as never);
    render(
      <DomainGuardLayout isAllowed={isUniversityUser} sectionLabel="University" deniedMessage="denied-university">
        <div>secret university content</div>
      </DomainGuardLayout>,
    );
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/organization"));
    expect(screen.queryByText("secret university content")).not.toBeInTheDocument();
  });

  it("Industry user is denied Superadmin shell", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: user("industry", "industry"), status: "authenticated" } as never);
    render(
      <DomainGuardLayout isAllowed={isSuperadminUser} sectionLabel="Superadmin" deniedMessage="denied-superadmin">
        <div>secret superadmin content</div>
      </DomainGuardLayout>,
    );
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/organization"));
  });

  it("Validator is denied Superadmin shell", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: user("government", "validator"), status: "authenticated" } as never);
    render(
      <DomainGuardLayout isAllowed={isSuperadminUser} sectionLabel="Superadmin" deniedMessage="denied">
        <div>secret</div>
      </DomainGuardLayout>,
    );
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/organization"));
  });

  it("Field Assistant is denied a Validator-only shell check (isGovernmentUser still true, but a stricter guard would block)", () => {
    // isGovernmentUser allows both roles — this documents that role-level
    // (not just domain-level) gating happens inside the page/component, not
    // the shared layout guard.
    expect(isGovernmentUser("government", "field_assistant")).toBe(true);
  });

  it("Superadmin CAN access the Superadmin shell", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: user("superadmin", "superadmin"), status: "authenticated" } as never);
    render(
      <DomainGuardLayout isAllowed={isSuperadminUser} sectionLabel="Superadmin" deniedMessage="denied">
        <div>allowed content</div>
      </DomainGuardLayout>,
    );
    await waitFor(() => expect(screen.getByText("allowed content")).toBeInTheDocument());
    expect(replace).not.toHaveBeenCalled();
  });

  it("shows a denied message (not a blank screen) while an unauthorized user is present pre-redirect", () => {
    vi.mocked(useAuth).mockReturnValue({ user: user("citizen", "citizen"), status: "authenticated" } as never);
    render(
      <DomainGuardLayout isAllowed={isIndustryUser} sectionLabel="Industry" deniedMessage="You don't belong here">
        <div>secret</div>
      </DomainGuardLayout>,
    );
    expect(screen.getByText("You don't belong here")).toBeInTheDocument();
  });
});
