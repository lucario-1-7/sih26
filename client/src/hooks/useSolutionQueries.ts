import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createSolution,
  getReplicationCandidates,
  getSolution,
  listSolutions,
  updateSolution,
} from "@/lib/api/solutions";
import type { SolutionCreateInput, SolutionUpdateInput } from "@/types/api";

export function useSolutionsList(params: { project_id?: string; cursor?: string | null } = {}) {
  return useQuery({
    queryKey: ["solutions", params],
    queryFn: () => listSolutions(params),
  });
}

export function useSolution(solutionId: string) {
  return useQuery({
    queryKey: ["solutions", solutionId],
    queryFn: () => getSolution(solutionId),
    enabled: Boolean(solutionId),
  });
}

export function useReplicationCandidates(solutionId: string) {
  return useQuery({
    queryKey: ["solutions", solutionId, "replication-candidates"],
    queryFn: () => getReplicationCandidates(solutionId),
    enabled: Boolean(solutionId),
  });
}

export function useCreateSolution() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SolutionCreateInput) => createSolution(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["solutions"] }),
  });
}

export function useUpdateSolution(solutionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SolutionUpdateInput) => updateSolution(solutionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["solutions", solutionId] });
      queryClient.invalidateQueries({ queryKey: ["solutions"] });
    },
  });
}
