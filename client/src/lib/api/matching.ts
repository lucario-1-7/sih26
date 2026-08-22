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
