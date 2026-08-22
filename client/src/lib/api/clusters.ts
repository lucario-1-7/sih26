import { apiFetch } from "@/lib/api/client";
import type { ClusterCreateInput, ClusterResponse, ClusterStatus, ClusterUpdateInput, PaginatedResponse } from "@/types/api";

/** Active clusters are the closest existing concept to "opportunities" for a
 * university — there is no dedicated opportunity-feed endpoint. See
 * client's project docs / final report for why this endpoint was chosen. */
export function listOpportunityClusters(params: {
  cursor?: string | null;
  limit?: number;
}): Promise<PaginatedResponse<ClusterResponse>> {
  return apiFetch<PaginatedResponse<ClusterResponse>>("/clusters", {
    query: { status: "active", cursor: params.cursor ?? undefined, limit: params.limit ?? 20 },
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
