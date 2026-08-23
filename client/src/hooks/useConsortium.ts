import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  confirmConsortium,
  getProjectConsortium,
  listConsortiumMembers,
  requestConsortium,
} from "@/lib/api/matching";

export function useProjectConsortium(projectId: string) {
  return useQuery({
    queryKey: ["consortium", "project", projectId],
    queryFn: () => getProjectConsortium(projectId),
    enabled: Boolean(projectId),
  });
}

export function useConsortiumMembers(consortiumId: string | undefined) {
  return useQuery({
    queryKey: ["consortium", "members", consortiumId],
    queryFn: () => listConsortiumMembers(consortiumId as string),
    enabled: Boolean(consortiumId),
  });
}

export function useRequestConsortium(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (teamSize: number) => requestConsortium(projectId, teamSize),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["consortium", "project", projectId] }),
  });
}

export function useConfirmConsortium(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (consortiumId: string) => confirmConsortium(consortiumId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["consortium", "project", projectId] }),
  });
}
