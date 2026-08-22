import { apiFetch } from "@/lib/api/client";
import type { DeliverableCreateInput, DeliverableResponse, DeliverableUpdateInput, PaginatedResponse } from "@/types/api";

export function listDeliverables(
  projectId: string,
  params: { cursor?: string | null; limit?: number } = {},
): Promise<PaginatedResponse<DeliverableResponse>> {
  return apiFetch<PaginatedResponse<DeliverableResponse>>(`/projects/${projectId}/deliverables`, {
    query: { cursor: params.cursor ?? undefined, limit: params.limit ?? 50 },
  });
}

export function createDeliverable(projectId: string, data: DeliverableCreateInput): Promise<DeliverableResponse> {
  return apiFetch<DeliverableResponse>(`/projects/${projectId}/deliverables`, { method: "POST", body: data });
}

export function updateDeliverable(
  projectId: string,
  deliverableId: string,
  data: DeliverableUpdateInput,
): Promise<DeliverableResponse> {
  return apiFetch<DeliverableResponse>(`/projects/${projectId}/deliverables/${deliverableId}`, {
    method: "PATCH",
    body: data,
  });
}

export function verifyDeliverable(
  projectId: string,
  deliverableId: string,
  approve: boolean,
): Promise<DeliverableResponse> {
  return apiFetch<DeliverableResponse>(`/projects/${projectId}/deliverables/${deliverableId}/verify`, {
    method: "POST",
    body: { approve },
  });
}
