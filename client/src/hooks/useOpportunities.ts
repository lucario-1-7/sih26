import { useQuery } from "@tanstack/react-query";

import { listOpportunityClusters } from "@/lib/api/clusters";

export function useOpportunities(params: { cursor?: string | null } = {}) {
  return useQuery({
    queryKey: ["opportunities", params],
    queryFn: () => listOpportunityClusters(params),
  });
}
