import { apiFetch } from "@/lib/api/client";
import type { DuplicateCandidateResponse, DuplicateDecisionCreateInput, DuplicateDecisionResponse } from "@/types/api";

export function listDuplicateCandidates(challengeId: string): Promise<DuplicateCandidateResponse[]> {
  return apiFetch<DuplicateCandidateResponse[]>(`/duplicate/challenges/${challengeId}/candidates`);
}

/** Validator-only. Append-only — this always creates a new decision record,
 * never mutates a prior one; a second call for the same pair is a
 * correction, not an error (see server/app/services/duplicate_service.py). */
export function createDuplicateDecision(data: DuplicateDecisionCreateInput): Promise<DuplicateDecisionResponse> {
  return apiFetch<DuplicateDecisionResponse>("/duplicate/decisions", { method: "POST", body: data });
}
