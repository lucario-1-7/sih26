import { apiFetch } from "@/lib/api/client";
import type { OrganizationCreateInput, OrganizationResponse, OrganizationType, PaginatedResponse } from "@/types/api";

export function listOrganizations(params: {
  cursor?: string;
  limit?: number;
  type?: OrganizationType;
} = {}): Promise<PaginatedResponse<OrganizationResponse>> {
  return apiFetch<PaginatedResponse<OrganizationResponse>>("/matching/organizations", {
    query: { cursor: params.cursor, limit: params.limit ?? 20, type: params.type },
  });
}

/** Superadmin only. */
export function createOrganization(data: OrganizationCreateInput): Promise<OrganizationResponse> {
  return apiFetch<OrganizationResponse>("/matching/organizations", { method: "POST", body: data });
}
