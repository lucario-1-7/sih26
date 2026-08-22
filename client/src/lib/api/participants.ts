import { apiFetch } from "@/lib/api/client";
import type {
  PaginatedResponse,
  ProjectParticipantCreateInput,
  ProjectParticipantResponse,
  ProjectParticipantUpdateInput,
} from "@/types/api";

export function listParticipants(
  projectId: string,
  params: { cursor?: string | null; limit?: number } = {},
): Promise<PaginatedResponse<ProjectParticipantResponse>> {
  return apiFetch<PaginatedResponse<ProjectParticipantResponse>>(`/projects/${projectId}/participants`, {
    query: { cursor: params.cursor ?? undefined, limit: params.limit ?? 50 },
  });
}

export function createParticipant(
  projectId: string,
  data: ProjectParticipantCreateInput,
): Promise<ProjectParticipantResponse> {
  return apiFetch<ProjectParticipantResponse>(`/projects/${projectId}/participants`, {
    method: "POST",
    body: data,
  });
}

export function updateParticipant(
  projectId: string,
  participantId: string,
  data: ProjectParticipantUpdateInput,
): Promise<ProjectParticipantResponse> {
  return apiFetch<ProjectParticipantResponse>(`/projects/${projectId}/participants/${participantId}`, {
    method: "PATCH",
    body: data,
  });
}
