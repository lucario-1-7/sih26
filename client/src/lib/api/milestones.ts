import { apiFetch } from "@/lib/api/client";
import type { MilestoneCreateInput, MilestoneResponse, MilestoneUpdateInput, PaginatedResponse } from "@/types/api";

export function listMilestones(
  projectId: string,
  params: { cursor?: string | null; limit?: number } = {},
): Promise<PaginatedResponse<MilestoneResponse>> {
  return apiFetch<PaginatedResponse<MilestoneResponse>>(`/projects/${projectId}/milestones`, {
    query: { cursor: params.cursor ?? undefined, limit: params.limit ?? 50 },
  });
}

export function createMilestone(projectId: string, data: MilestoneCreateInput): Promise<MilestoneResponse> {
  return apiFetch<MilestoneResponse>(`/projects/${projectId}/milestones`, { method: "POST", body: data });
}

export function updateMilestone(
  projectId: string,
  milestoneId: string,
  data: MilestoneUpdateInput,
): Promise<MilestoneResponse> {
  return apiFetch<MilestoneResponse>(`/projects/${projectId}/milestones/${milestoneId}`, {
    method: "PATCH",
    body: data,
  });
}
