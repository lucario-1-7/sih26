import { apiFetch } from "@/lib/api/client";
import type { Domain, PaginatedResponse, Role, UserCreateInput, UserResponse, UserUpdateInput } from "@/types/api";

/** Superadmin only. */
export function listUsers(params: {
  cursor?: string;
  limit?: number;
  role?: Role;
} = {}): Promise<PaginatedResponse<UserResponse>> {
  return apiFetch<PaginatedResponse<UserResponse>>("/users", {
    query: { cursor: params.cursor, limit: params.limit ?? 20, role: params.role },
  });
}

/** Superadmin only. Provisions a login for GOVERNMENT/UNIVERSITY/INDUSTRY/
 * SUPERADMIN staff — CITIZEN accounts self-provision via OTP instead. */
export function createUser(data: UserCreateInput): Promise<UserResponse> {
  return apiFetch<UserResponse>("/users", { method: "POST", body: data });
}

/** Superadmin only. The backend rejects a Superadmin editing their own
 * role/domain/organization (self-modification guard) — that 403 is
 * surfaced to the caller, never bypassed client-side. */
export function updateUser(userId: string, data: UserUpdateInput): Promise<UserResponse> {
  return apiFetch<UserResponse>(`/users/${userId}`, { method: "PATCH", body: data });
}

export const ALL_DOMAINS: Domain[] = ["citizen", "government", "university", "industry", "superadmin"];
