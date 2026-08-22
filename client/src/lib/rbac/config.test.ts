import { describe, expect, it } from "vitest";

import {
  canCreateCommitment,
  canCreateProject,
  canManageClustersThemes,
  canManageOrganizations,
  canManageUsers,
  canMakeDuplicateDecision,
  canProposeCollaboration,
  canPublishSolution,
  canReviewCollaboration,
  canReviewCommitment,
  canSetSeverity,
  canSubmitAssisted,
  canVerifyDeliverable,
  canVerifyImpact,
  canViewAnalytics,
  coordinatorNav,
  facultyNav,
  fieldAssistantNav,
  industryNav,
  isGovernmentUser,
  isIndustryUser,
  isSuperadminUser,
  isUniversityUser,
  navForRole,
  superadminNav,
  validatorNav,
} from "@/lib/rbac/config";

describe("domain/role isX guards — cross-domain isolation", () => {
  it("University: only coordinator/faculty under domain=university", () => {
    expect(isUniversityUser("university", "coordinator")).toBe(true);
    expect(isUniversityUser("university", "faculty")).toBe(true);
    expect(isUniversityUser("government", "validator")).toBe(false);
    expect(isUniversityUser("industry", "industry")).toBe(false);
    expect(isUniversityUser("citizen", "citizen")).toBe(false);
    expect(isUniversityUser("superadmin", "superadmin")).toBe(false);
  });

  it("Government: only validator/field_assistant under domain=government", () => {
    expect(isGovernmentUser("government", "validator")).toBe(true);
    expect(isGovernmentUser("government", "field_assistant")).toBe(true);
    expect(isGovernmentUser("university", "coordinator")).toBe(false);
    expect(isGovernmentUser("industry", "industry")).toBe(false);
    expect(isGovernmentUser("superadmin", "superadmin")).toBe(false);
  });

  it("Industry: only industry under domain=industry", () => {
    expect(isIndustryUser("industry", "industry")).toBe(true);
    expect(isIndustryUser("government", "validator")).toBe(false);
    expect(isIndustryUser("university", "faculty")).toBe(false);
    expect(isIndustryUser("superadmin", "superadmin")).toBe(false);
  });

  it("Superadmin: only superadmin under domain=superadmin", () => {
    expect(isSuperadminUser("superadmin", "superadmin")).toBe(true);
    expect(isSuperadminUser("government", "validator")).toBe(false);
    expect(isSuperadminUser("industry", "industry")).toBe(false);
    expect(isSuperadminUser("university", "coordinator")).toBe(false);
  });
});

describe("navForRole", () => {
  it("maps every organizational role to its own nav", () => {
    expect(navForRole("coordinator")).toEqual(coordinatorNav());
    expect(navForRole("faculty")).toEqual(facultyNav());
    expect(navForRole("validator")).toEqual(validatorNav());
    expect(navForRole("field_assistant")).toEqual(fieldAssistantNav());
    expect(navForRole("industry")).toEqual(industryNav());
    expect(navForRole("superadmin")).toEqual(superadminNav());
  });

  it("returns empty nav for citizen (no organizational dashboard)", () => {
    expect(navForRole("citizen")).toEqual([]);
  });

  it("Field Assistant nav has no duplicate-decision or severity entry points", () => {
    const labels = fieldAssistantNav().map((i) => i.label.toLowerCase());
    expect(labels.some((l) => l.includes("duplicate"))).toBe(false);
    expect(labels.some((l) => l.includes("severity"))).toBe(false);
  });

  it("Validator nav includes Challenges/Clusters/Themes management entry points", () => {
    const labels = validatorNav().map((i) => i.label);
    expect(labels).toContain("Challenges");
    expect(labels).toContain("Clusters");
    expect(labels).toContain("Themes");
  });

  it("Superadmin nav includes Users/Organizations/Analytics/Model Info", () => {
    const labels = superadminNav().map((i) => i.label);
    expect(labels).toEqual(
      expect.arrayContaining(["Users", "Organizations", "Analytics", "Model Info"]),
    );
  });
});

describe("RBAC capability matrix — Government: Validator vs Field Assistant", () => {
  it("Challenge review: both can view; only Validator mutates severity", () => {
    expect(canSetSeverity("validator")).toBe(true);
    expect(canSetSeverity("field_assistant")).toBe(false);
  });

  it("Duplicate decision: Validator YES, Field Assistant NO", () => {
    expect(canMakeDuplicateDecision("validator")).toBe(true);
    expect(canMakeDuplicateDecision("field_assistant")).toBe(false);
  });

  it("Impact verification: Validator YES, Field Assistant NO", () => {
    expect(canVerifyImpact("validator")).toBe(true);
    expect(canVerifyImpact("field_assistant")).toBe(false);
  });

  it("Assisted submission: Field Assistant YES, Validator NO", () => {
    expect(canSubmitAssisted("field_assistant")).toBe(true);
    expect(canSubmitAssisted("validator")).toBe(false);
  });

  it("Cluster/theme management: Validator YES, Field Assistant NO", () => {
    expect(canManageClustersThemes("validator")).toBe(true);
    expect(canManageClustersThemes("field_assistant")).toBe(false);
  });
});

describe("RBAC capability matrix — Industry vs Superadmin", () => {
  it("Collaboration proposal: Industry YES, Superadmin NO (superadmin has visibility, not the industry-side action)", () => {
    expect(canProposeCollaboration("industry")).toBe(true);
    expect(canProposeCollaboration("superadmin")).toBe(false);
  });

  it("Collaboration review/accept: university-side roles + Superadmin, not Industry", () => {
    expect(canReviewCollaboration("coordinator")).toBe(true);
    expect(canReviewCollaboration("faculty")).toBe(true);
    expect(canReviewCollaboration("superadmin")).toBe(true);
    expect(canReviewCollaboration("industry")).toBe(false);
  });

  it("Commitments: Industry creates, university-side reviews", () => {
    expect(canCreateCommitment("industry")).toBe(true);
    expect(canCreateCommitment("coordinator")).toBe(false);
    expect(canReviewCommitment("coordinator")).toBe(true);
    expect(canReviewCommitment("industry")).toBe(false);
  });

  it("User management: Superadmin only", () => {
    expect(canManageUsers("superadmin")).toBe(true);
    expect(canManageUsers("industry")).toBe(false);
    expect(canManageUsers("validator")).toBe(false);
    expect(canManageUsers("coordinator")).toBe(false);
  });

  it("Analytics: Superadmin only", () => {
    expect(canViewAnalytics("superadmin")).toBe(true);
    expect(canViewAnalytics("industry")).toBe(false);
    expect(canViewAnalytics("validator")).toBe(false);
  });

  it("Organization management: Superadmin only (industry has no self-service org edit endpoint)", () => {
    expect(canManageOrganizations("superadmin")).toBe(true);
    expect(canManageOrganizations("industry")).toBe(false);
  });
});

describe("University capability flags (regression — must still work)", () => {
  it("Project creation: coordinator or superadmin", () => {
    expect(canCreateProject("coordinator")).toBe(true);
    expect(canCreateProject("superadmin")).toBe(true);
    expect(canCreateProject("faculty")).toBe(false);
  });

  it("Deliverable verification: coordinator or superadmin, not faculty", () => {
    expect(canVerifyDeliverable("coordinator")).toBe(true);
    expect(canVerifyDeliverable("faculty")).toBe(false);
  });

  it("Solution publish: coordinator or faculty", () => {
    expect(canPublishSolution("coordinator")).toBe(true);
    expect(canPublishSolution("faculty")).toBe(true);
    expect(canPublishSolution("industry")).toBe(false);
  });
});
