import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createCluster, listClusters, updateCluster } from "@/lib/api/clusters";
import { createTheme, listThemes, updateTheme } from "@/lib/api/themes";
import type { ClusterCreateInput, ClusterStatus, ClusterUpdateInput, ThemeCreateInput, ThemeUpdateInput } from "@/types/api";

export function useClustersList(params: { status?: ClusterStatus; cursor?: string } = {}) {
  return useQuery({ queryKey: ["clusters", params], queryFn: () => listClusters(params) });
}

export function useCreateCluster() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ClusterCreateInput) => createCluster(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["clusters"] }),
  });
}

export function useUpdateCluster(clusterId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ClusterUpdateInput) => updateCluster(clusterId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["clusters"] }),
  });
}

export function useThemesList(params: { cursor?: string } = {}) {
  return useQuery({ queryKey: ["themes", params], queryFn: () => listThemes(params) });
}

export function useCreateTheme() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ThemeCreateInput) => createTheme(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["themes"] }),
  });
}

export function useUpdateTheme(themeId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ThemeUpdateInput) => updateTheme(themeId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["themes"] }),
  });
}
