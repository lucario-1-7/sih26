import { apiFetch } from "@/lib/api/client";
import type {
  ChallengeResponse,
  ChallengeStatus,
  ChallengeUpdateInput,
  PaginatedResponse,
} from "@/types/api";

export function listChallenges(params: {
  cursor?: string;
  limit?: number;
  status?: ChallengeStatus;
  cluster_id?: string;
  submitted_by_id?: string;
}): Promise<PaginatedResponse<ChallengeResponse>> {
  return apiFetch<PaginatedResponse<ChallengeResponse>>("/challenges", {
    query: {
      cursor: params.cursor,
      limit: params.limit ?? 20,
      status: params.status,
      cluster_id: params.cluster_id,
      submitted_by_id: params.submitted_by_id,
    },
  });
}

export function getChallenge(challengeId: string): Promise<ChallengeResponse> {
  return apiFetch<ChallengeResponse>(`/challenges/${challengeId}`);
}

export function updateChallenge(challengeId: string, data: ChallengeUpdateInput): Promise<ChallengeResponse> {
  return apiFetch<ChallengeResponse>(`/challenges/${challengeId}`, { method: "PATCH", body: data });
}

export interface AssistedChallengeCreateInput {
  title: string;
  description: string;
  administrative_area_id: string;
  pin_code?: string | null;
  on_behalf_of_name: string;
  on_behalf_of_phone: string;
}

export function createAssistedChallenge(data: AssistedChallengeCreateInput): Promise<ChallengeResponse> {
  return apiFetch<ChallengeResponse>("/challenges", { method: "POST", body: data });
}
