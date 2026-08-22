import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createDeliverable,
  listDeliverables,
  updateDeliverable,
  verifyDeliverable,
} from "@/lib/api/deliverables";
import { createMilestone, listMilestones, updateMilestone } from "@/lib/api/milestones";
import { createParticipant, listParticipants, updateParticipant } from "@/lib/api/participants";
import { createProject, getProject, listProjects, updateProject } from "@/lib/api/projects";
import type {
  DeliverableCreateInput,
  DeliverableUpdateInput,
  MilestoneCreateInput,
  MilestoneUpdateInput,
  ProjectCreateInput,
  ProjectParticipantCreateInput,
  ProjectParticipantUpdateInput,
  ProjectStatus,
  ProjectUpdateInput,
} from "@/types/api";

export function useProjectsList(params: { status?: ProjectStatus; cursor?: string | null } = {}) {
  return useQuery({
    queryKey: ["projects", params],
    queryFn: () => listProjects(params),
  });
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => getProject(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProjectCreateInput) => createProject(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useUpdateProject(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProjectUpdateInput) => updateProject(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useMilestonesList(projectId: string) {
  return useQuery({
    queryKey: ["milestones", projectId],
    queryFn: () => listMilestones(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCreateMilestone(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: MilestoneCreateInput) => createMilestone(projectId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["milestones", projectId] }),
  });
}

export function useUpdateMilestone(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ milestoneId, data }: { milestoneId: string; data: MilestoneUpdateInput }) =>
      updateMilestone(projectId, milestoneId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["milestones", projectId] }),
  });
}

export function useDeliverablesList(projectId: string) {
  return useQuery({
    queryKey: ["deliverables", projectId],
    queryFn: () => listDeliverables(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCreateDeliverable(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DeliverableCreateInput) => createDeliverable(projectId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["deliverables", projectId] }),
  });
}

export function useUpdateDeliverable(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ deliverableId, data }: { deliverableId: string; data: DeliverableUpdateInput }) =>
      updateDeliverable(projectId, deliverableId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["deliverables", projectId] }),
  });
}

export function useVerifyDeliverable(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ deliverableId, approve }: { deliverableId: string; approve: boolean }) =>
      verifyDeliverable(projectId, deliverableId, approve),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["deliverables", projectId] }),
  });
}

export function useParticipantsList(projectId: string) {
  return useQuery({
    queryKey: ["participants", projectId],
    queryFn: () => listParticipants(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCreateParticipant(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProjectParticipantCreateInput) => createParticipant(projectId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["participants", projectId] }),
  });
}

export function useUpdateParticipant(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ participantId, data }: { participantId: string; data: ProjectParticipantUpdateInput }) =>
      updateParticipant(projectId, participantId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["participants", projectId] }),
  });
}
