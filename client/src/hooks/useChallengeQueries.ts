import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAssistedChallenge, getChallenge, listChallenges, updateChallenge } from "@/lib/api/challenges";
import { createDuplicateDecision, listDuplicateCandidates } from "@/lib/api/duplicate";
import type {
  AssistedChallengeCreateInput,
} from "@/lib/api/challenges";
import type { ChallengeStatus, ChallengeUpdateInput, DuplicateDecisionCreateInput } from "@/types/api";

export function useChallengesList(params: { status?: ChallengeStatus; cursor?: string } = {}) {
  return useQuery({
    queryKey: ["challenges", params],
    queryFn: () => listChallenges(params),
  });
}

export function useChallenge(challengeId: string) {
  return useQuery({
    queryKey: ["challenges", challengeId],
    queryFn: () => getChallenge(challengeId),
    enabled: Boolean(challengeId),
  });
}

export function useUpdateChallenge(challengeId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ChallengeUpdateInput) => updateChallenge(challengeId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["challenges", challengeId] });
      queryClient.invalidateQueries({ queryKey: ["challenges"] });
    },
  });
}

export function useCreateAssistedChallenge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AssistedChallengeCreateInput) => createAssistedChallenge(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["challenges"] }),
  });
}

export function useDuplicateCandidates(challengeId: string) {
  return useQuery({
    queryKey: ["duplicate-candidates", challengeId],
    queryFn: () => listDuplicateCandidates(challengeId),
    enabled: Boolean(challengeId),
  });
}

export function useCreateDuplicateDecision(challengeId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DuplicateDecisionCreateInput) => createDuplicateDecision(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["challenges", challengeId] });
      queryClient.invalidateQueries({ queryKey: ["duplicate-candidates", challengeId] });
    },
  });
}
