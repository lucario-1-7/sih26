import { apiFetch } from "@/lib/api/client";
import type { ConsortiumMemberResponse, ConsortiumResponse, MatchResult, OrganizationType } from "@/types/api";

/** AI-assisted recommendation, not a definitive match — see MatchResult's
 * `rationale`/`breakdown`. Validator/Coordinator/Superadmin only. */
export function matchOrganizationsForCluster(clusterId: string, orgType?: OrganizationType): Promise<MatchResult[]> {
  return apiFetch<MatchResult[]>(`/matching/clusters/${clusterId}`, {
    query: { type: orgType },
  });
}

export function getProjectConsortium(projectId: string): Promise<ConsortiumResponse | null> {
  return apiFetch<ConsortiumResponse | null>(`/matching/projects/${projectId}/consortium`);
}

export function listConsortiumMembers(consortiumId: string): Promise<ConsortiumMemberResponse[]> {
  return apiFetch<ConsortiumMemberResponse[]>(`/matching/consortiums/${consortiumId}/members`);
}

/** Queues ML consortium formation (async — ML ranks, server persists). Coordinator/Faculty/Superadmin only. */
export function requestConsortium(projectId: string, teamSize = 3): Promise<{ detail: string }> {
  return apiFetch<{ detail: string }>(`/matching/projects/${projectId}/consortium`, {
    method: "POST",
    body: { team_size: teamSize },
  });
}

/** Human confirmation of a proposed consortium — the authoritative decision, not the ML suggestion. */
export function confirmConsortium(consortiumId: string): Promise<ConsortiumResponse> {
  return apiFetch<ConsortiumResponse>(`/matching/consortiums/${consortiumId}/confirm`, {
    method: "PATCH",
  });
}
