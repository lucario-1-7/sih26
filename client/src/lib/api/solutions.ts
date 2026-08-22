import { apiFetch } from "@/lib/api/client";
import type {
  PaginatedResponse,
  ReplicationCandidateResponse,
  SolutionCreateInput,
  SolutionResponse,
  SolutionUpdateInput,
} from "@/types/api";

export function listSolutions(params: {
  cursor?: string | null;
  limit?: number;
  project_id?: string;
}): Promise<PaginatedResponse<SolutionResponse>> {
  return apiFetch<PaginatedResponse<SolutionResponse>>("/solutions", {
    query: { cursor: params.cursor ?? undefined, limit: params.limit ?? 20, project_id: params.project_id },
  });
}

export function getSolution(solutionId: string): Promise<SolutionResponse> {
  return apiFetch<SolutionResponse>(`/solutions/${solutionId}`);
}

export function createSolution(data: SolutionCreateInput): Promise<SolutionResponse> {
  return apiFetch<SolutionResponse>("/solutions", { method: "POST", body: data });
}

export function updateSolution(solutionId: string, data: SolutionUpdateInput): Promise<SolutionResponse> {
  return apiFetch<SolutionResponse>(`/solutions/${solutionId}`, { method: "PATCH", body: data });
}

export function getReplicationCandidates(solutionId: string): Promise<ReplicationCandidateResponse[]> {
  return apiFetch<ReplicationCandidateResponse[]>(`/solutions/${solutionId}/replication-candidates`);
}
