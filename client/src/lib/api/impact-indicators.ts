import { apiFetch } from "@/lib/api/client";
import type { ImpactIndicatorCreateInput, ImpactIndicatorEndlineInput, ImpactIndicatorResponse, PaginatedResponse } from "@/types/api";

export function listImpactIndicators(
  projectId: string,
  params: { cursor?: string; limit?: number } = {},
): Promise<PaginatedResponse<ImpactIndicatorResponse>> {
  return apiFetch<PaginatedResponse<ImpactIndicatorResponse>>(`/projects/${projectId}/impact-indicators`, {
    query: { cursor: params.cursor, limit: params.limit ?? 50 },
  });
}

/** Faculty/Coordinator/Superadmin — declares the baseline before implementation. */
export function createImpactIndicator(
  projectId: string,
  data: ImpactIndicatorCreateInput,
): Promise<ImpactIndicatorResponse> {
  return apiFetch<ImpactIndicatorResponse>(`/projects/${projectId}/impact-indicators`, {
    method: "POST",
    body: data,
  });
}

/** Faculty/Coordinator/Superadmin — the claimed (unverified) endline. */
export function submitEndline(
  projectId: string,
  indicatorId: string,
  data: ImpactIndicatorEndlineInput,
): Promise<ImpactIndicatorResponse> {
  return apiFetch<ImpactIndicatorResponse>(`/projects/${projectId}/impact-indicators/${indicatorId}/endline`, {
    method: "PATCH",
    body: data,
  });
}

/** Validator/Superadmin only — independent verification, distinct from the claim. */
export function verifyImpactIndicator(
  projectId: string,
  indicatorId: string,
  approve: boolean,
): Promise<ImpactIndicatorResponse> {
  return apiFetch<ImpactIndicatorResponse>(`/projects/${projectId}/impact-indicators/${indicatorId}/verify`, {
    method: "POST",
    body: { approve },
  });
}
