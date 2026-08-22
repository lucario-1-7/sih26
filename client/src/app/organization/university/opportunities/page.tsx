"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useOpportunities } from "@/hooks/useOpportunities";
import { useAuth } from "@/hooks/useAuth";
import { useCreateProject } from "@/hooks/useProjectQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { canCreateProject } from "@/lib/rbac/config";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import type { ClusterResponse } from "@/types/api";

export default function OpportunitiesPage() {
  const { user } = useAuth();
  const pagination = useCursorPagination<ClusterResponse>();
  const query = useOpportunities({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);

  const createProject = useCreateProject();
  const router = useRouter();
  const [creatingClusterId, setCreatingClusterId] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);

  async function handleCreateProject(clusterId: string, clusterTitle: string) {
    setCreatingClusterId(clusterId);
    setCreateError(null);
    try {
      const project = await createProject.mutateAsync({ cluster_id: clusterId, title: clusterTitle });
      router.push(`/organization/university/projects/${project.id}`);
    } catch (err) {
      setCreateError(errorMessage(err));
    } finally {
      setCreatingClusterId(null);
    }
  }

  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  return (
    <div>
      <PageHeader
        title="Opportunities"
        description="Active systemic-problem clusters your institution could propose a project against."
      />

      {createError ? (
        <div role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          {createError}
        </div>
      ) : null}

      {showInitialLoading ? (
        <Spinner label="Loading opportunities…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No open opportunities" description="Check back later for newly clustered challenges." />
      ) : (
        <div className="flex flex-col gap-3">
          {pagination.items.map((cluster) => (
            <Card key={cluster.id} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">{cluster.title}</p>
                {cluster.description ? <p className="mt-1 text-sm text-slate-500">{cluster.description}</p> : null}
              </div>
              {user && canCreateProject(user.role) ? (
                <Button
                  onClick={() => void handleCreateProject(cluster.id, cluster.title)}
                  disabled={creatingClusterId === cluster.id}
                >
                  {creatingClusterId === cluster.id ? "Creating…" : "Propose project"}
                </Button>
              ) : null}
            </Card>
          ))}
        </div>
      )}

      {pagination.hasNext && pagination.items.length > 0 ? (
        <div className="mt-4 flex justify-center">
          <Button variant="secondary" onClick={pagination.loadMore} disabled={query.isFetching}>
            {query.isFetching ? "Loading…" : "Load more"}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
