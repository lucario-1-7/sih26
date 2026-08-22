import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createImpactIndicator, listImpactIndicators, submitEndline, verifyImpactIndicator } from "@/lib/api/impact-indicators";
import type { ImpactIndicatorCreateInput, ImpactIndicatorEndlineInput } from "@/types/api";

export function useImpactIndicatorsList(projectId: string) {
  return useQuery({
    queryKey: ["impact-indicators", projectId],
    queryFn: () => listImpactIndicators(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCreateImpactIndicator(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ImpactIndicatorCreateInput) => createImpactIndicator(projectId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["impact-indicators", projectId] }),
  });
}

export function useSubmitEndline(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ indicatorId, data }: { indicatorId: string; data: ImpactIndicatorEndlineInput }) =>
      submitEndline(projectId, indicatorId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["impact-indicators", projectId] }),
  });
}

export function useVerifyImpactIndicator(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ indicatorId, approve }: { indicatorId: string; approve: boolean }) =>
      verifyImpactIndicator(projectId, indicatorId, approve),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["impact-indicators", projectId] }),
  });
}
