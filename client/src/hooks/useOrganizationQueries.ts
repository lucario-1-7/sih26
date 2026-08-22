import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createOrganization, listOrganizations } from "@/lib/api/organizations";
import type { OrganizationCreateInput, OrganizationType } from "@/types/api";

export function useOrganizationsList(params: { type?: OrganizationType; cursor?: string } = {}) {
  return useQuery({ queryKey: ["organizations", params], queryFn: () => listOrganizations(params) });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OrganizationCreateInput) => createOrganization(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["organizations"] }),
  });
}
