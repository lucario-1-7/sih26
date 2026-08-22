import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCollaboration,
  createCommitment,
  listCollaborations,
  listCommitments,
  updateCollaborationStatus,
  updateCommitmentStatus,
} from "@/lib/api/collaborations";
import type {
  CollaborationCreateInput,
  CollaborationStatusUpdateInput,
  CommitmentCreateInput,
  CommitmentStatusUpdateInput,
} from "@/types/api";

export function useCollaborationsList(params: { project_id?: string; cursor?: string } = {}) {
  return useQuery({
    queryKey: ["collaborations", params],
    queryFn: () => listCollaborations(params),
  });
}

export function useCreateCollaboration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CollaborationCreateInput) => createCollaboration(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["collaborations"] }),
  });
}

export function useUpdateCollaborationStatus(collaborationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CollaborationStatusUpdateInput) => updateCollaborationStatus(collaborationId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["collaborations"] }),
  });
}

export function useCommitmentsList(collaborationId: string) {
  return useQuery({
    queryKey: ["commitments", collaborationId],
    queryFn: () => listCommitments(collaborationId),
    enabled: Boolean(collaborationId),
  });
}

export function useCreateCommitment(collaborationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CommitmentCreateInput) => createCommitment(collaborationId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["commitments", collaborationId] }),
  });
}

export function useUpdateCommitmentStatus(collaborationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ commitmentId, data }: { commitmentId: string; data: CommitmentStatusUpdateInput }) =>
      updateCommitmentStatus(collaborationId, commitmentId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["commitments", collaborationId] }),
  });
}
