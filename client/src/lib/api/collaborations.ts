import { apiFetch } from "@/lib/api/client";
import type {
  CollaborationCreateInput,
  CollaborationResponse,
  CollaborationStatusUpdateInput,
  CommitmentCreateInput,
  CommitmentResponse,
  CommitmentStatusUpdateInput,
  PaginatedResponse,
} from "@/types/api";

/** Industry only. organization_id is always derived server-side from the
 * caller — never client-supplied. */
export function createCollaboration(data: CollaborationCreateInput): Promise<CollaborationResponse> {
  return apiFetch<CollaborationResponse>("/collaborations", { method: "POST", body: data });
}

/** Pass `project_id` for the university/government view (all collaborations
 * on a project); omit it for the industry view (the caller's own org). */
export function listCollaborations(params: {
  project_id?: string;
  cursor?: string;
  limit?: number;
} = {}): Promise<PaginatedResponse<CollaborationResponse>> {
  return apiFetch<PaginatedResponse<CollaborationResponse>>("/collaborations", {
    query: { project_id: params.project_id, cursor: params.cursor, limit: params.limit ?? 20 },
  });
}

/** Industry proposes (interested->proposed); University/Superadmin
 * accept/reject/activate/complete. The backend enforces which side may
 * perform which transition — see COLLABORATION_STATUS_TRANSITIONS. */
export function updateCollaborationStatus(
  collaborationId: string,
  data: CollaborationStatusUpdateInput,
): Promise<CollaborationResponse> {
  return apiFetch<CollaborationResponse>(`/collaborations/${collaborationId}/status`, {
    method: "PATCH",
    body: data,
  });
}

/** Industry only. */
export function createCommitment(collaborationId: string, data: CommitmentCreateInput): Promise<CommitmentResponse> {
  return apiFetch<CommitmentResponse>(`/collaborations/${collaborationId}/commitments`, {
    method: "POST",
    body: data,
  });
}

export function listCommitments(
  collaborationId: string,
  params: { cursor?: string; limit?: number } = {},
): Promise<PaginatedResponse<CommitmentResponse>> {
  return apiFetch<PaginatedResponse<CommitmentResponse>>(`/collaborations/${collaborationId}/commitments`, {
    query: { cursor: params.cursor, limit: params.limit ?? 20 },
  });
}

/** University/Superadmin only — Industry proposes a commitment, the
 * university side reviews it. */
export function updateCommitmentStatus(
  collaborationId: string,
  commitmentId: string,
  data: CommitmentStatusUpdateInput,
): Promise<CommitmentResponse> {
  return apiFetch<CommitmentResponse>(`/collaborations/${collaborationId}/commitments/${commitmentId}/status`, {
    method: "PATCH",
    body: data,
  });
}
