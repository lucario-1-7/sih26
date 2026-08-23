import type { Domain, Role } from "@/types/api";

// Centralized frontend RBAC config. This is UX-only — routing/navigation/
// visibility. The backend is the actual authorization boundary; a hidden nav
// item here does not stand in for a server-side permission check.

export interface NavItem {
  label: string;
  href: string;
}

export const UNIVERSITY_ROLES: Role[] = ["coordinator", "faculty"];
export const GOVERNMENT_ROLES: Role[] = ["validator", "field_assistant"];
export const INDUSTRY_ROLES: Role[] = ["industry"];
export const SUPERADMIN_ROLES: Role[] = ["superadmin"];

export function isUniversityUser(domain: Domain, role: Role): boolean {
  return domain === "university" && UNIVERSITY_ROLES.includes(role);
}

export function isGovernmentUser(domain: Domain, role: Role): boolean {
  return domain === "government" && GOVERNMENT_ROLES.includes(role);
}

export function isIndustryUser(domain: Domain, role: Role): boolean {
  return domain === "industry" && INDUSTRY_ROLES.includes(role);
}

export function isSuperadminUser(domain: Domain, role: Role): boolean {
  return domain === "superadmin" && SUPERADMIN_ROLES.includes(role);
}

export function coordinatorNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/organization/university" },
    { label: "Opportunities", href: "/organization/university/opportunities" },
    { label: "Projects", href: "/organization/university/projects" },
    { label: "Solutions", href: "/organization/university/solutions" },
    { label: "Profile", href: "/organization/university/profile" },
  ];
}

export function facultyNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/organization/university" },
    { label: "My Projects", href: "/organization/university/projects?mine=true" },
    { label: "Projects", href: "/organization/university/projects" },
    { label: "Solutions", href: "/organization/university/solutions" },
    { label: "Profile", href: "/organization/university/profile" },
  ];
}

export function validatorNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/organization/government" },
    { label: "Pending Triage", href: "/organization/government/challenges/pending-triage" },
    { label: "Challenges", href: "/organization/government/challenges" },
    { label: "Clusters", href: "/organization/government/clusters" },
    { label: "Themes", href: "/organization/government/themes" },
    { label: "Projects", href: "/organization/government/projects" },
    { label: "Profile", href: "/organization/government/profile" },
  ];
}

export function fieldAssistantNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/organization/government" },
    { label: "Submit for Citizen", href: "/organization/government/assisted-submission" },
    { label: "My Assisted Cases", href: "/organization/government/challenges?mine=true" },
    { label: "Profile", href: "/organization/government/profile" },
  ];
}

export function industryNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/organization/industry" },
    { label: "Opportunities", href: "/organization/industry/opportunities" },
    { label: "Collaborations", href: "/organization/industry/collaborations" },
    { label: "Profile", href: "/organization/industry/profile" },
  ];
}

export function superadminNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/organization/superadmin" },
    { label: "Users", href: "/organization/superadmin/users" },
    { label: "Organizations", href: "/organization/superadmin/organizations" },
    { label: "Analytics", href: "/organization/superadmin/analytics" },
    { label: "Model Info", href: "/organization/superadmin/model-info" },
    { label: "Profile", href: "/organization/superadmin/profile" },
  ];
}

export function navForRole(role: Role): NavItem[] {
  switch (role) {
    case "coordinator":
      return coordinatorNav();
    case "faculty":
      return facultyNav();
    case "validator":
      return validatorNav();
    case "field_assistant":
      return fieldAssistantNav();
    case "industry":
      return industryNav();
    case "superadmin":
      return superadminNav();
    default:
      return [];
  }
}

/** Capability flags — used to hide actions the role cannot perform, kept in
 * one place instead of scattered role checks in JSX. Mirrors the backend's
 * actual RBAC (see server/app/api/v1/*) — the backend re-enforces every one
 * of these independently; a flag here only controls what a button renders. */

// University
export function canCreateProject(role: Role): boolean {
  return role === "coordinator" || role === "superadmin";
}

export function canVerifyDeliverable(role: Role): boolean {
  return role === "coordinator" || role === "superadmin";
}

export function canPublishSolution(role: Role): boolean {
  return role === "coordinator" || role === "faculty" || role === "superadmin";
}

export function canManageProjectContent(role: Role): boolean {
  return role === "coordinator" || role === "faculty" || role === "superadmin";
}

// Government
export function canMakeDuplicateDecision(role: Role): boolean {
  return role === "validator";
}

export function canSetSeverity(role: Role): boolean {
  return role === "validator";
}

export function canManageClustersThemes(role: Role): boolean {
  return role === "validator" || role === "superadmin";
}

export function canSubmitAssisted(role: Role): boolean {
  return role === "field_assistant";
}

export function canVerifyImpact(role: Role): boolean {
  return role === "validator" || role === "superadmin";
}

// Industry
export function canProposeCollaboration(role: Role): boolean {
  return role === "industry";
}

export function canReviewCollaboration(role: Role): boolean {
  return role === "coordinator" || role === "faculty" || role === "superadmin";
}

export function canCreateCommitment(role: Role): boolean {
  return role === "industry";
}

export function canReviewCommitment(role: Role): boolean {
  return role === "coordinator" || role === "faculty" || role === "superadmin";
}

// Superadmin
export function canManageUsers(role: Role): boolean {
  return role === "superadmin";
}

export function canManageOrganizations(role: Role): boolean {
  return role === "superadmin";
}

export function canViewAnalytics(role: Role): boolean {
  return role === "superadmin";
}
