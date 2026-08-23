import { apiFetch } from "@/lib/api/client";
import type { ClusterCreateInput, ClusterResponse, ClusterStatus, ClusterUpdateInput, PaginatedResponse } from "@/types/api";

/** Active, unclaimed clusters (no Project yet) are "opportunities" - a
 * cluster a university/coordinator could actually propose a project
 * against. `unclaimed=true` excludes clusters another organization has
 * already turned into a project; there is no separate opportunity-feed
 * endpoint, this is the canonical /clusters listing with that filter. */
export function listOpportunityClusters(params: {
  cursor?: string | null;
  limit?: number;
}): Promise<PaginatedResponse<ClusterResponse>> {
  return apiFetch<PaginatedResponse<ClusterResponse>>("/clusters", {
    query: { status: "active", unclaimed: true, cursor: params.cursor ?? undefined, limit: params.limit ?? 20 },
  });
}

export function getCluster(clusterId: string): Promise<ClusterResponse> {
  return apiFetch<ClusterResponse>(`/clusters/${clusterId}`);
}

export function listClusters(params: {
  cursor?: string;
  limit?: number;
  status?: ClusterStatus;
} = {}): Promise<PaginatedResponse<ClusterResponse>> {
  return apiFetch<PaginatedResponse<ClusterResponse>>("/clusters", {
    query: { cursor: params.cursor, limit: params.limit ?? 20, status: params.status },
  });
}

/** Validator/Superadmin only. */
export function createCluster(data: ClusterCreateInput): Promise<ClusterResponse> {
  return apiFetch<ClusterResponse>("/clusters", { method: "POST", body: data });
}

/** Validator/Superadmin only. */
export function updateCluster(clusterId: string, data: ClusterUpdateInput): Promise<ClusterResponse> {
  return apiFetch<ClusterResponse>(`/clusters/${clusterId}`, { method: "PATCH", body: data });
}
