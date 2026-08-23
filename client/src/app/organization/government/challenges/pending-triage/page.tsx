"use client";

import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useChallengesList, useUpdateChallenge } from "@/hooks/useChallengeQueries";
import { useClustersList } from "@/hooks/useThemeClusterQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { canManageClustersThemes } from "@/lib/rbac/config";
import { errorMessage } from "@/components/ui/ErrorState";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ChallengeResponse } from "@/types/api";

function TriageRow({ challenge, canCluster }: { challenge: ChallengeResponse; canCluster: boolean }) {
  const clustersQuery = useClustersList();
  const updateChallenge = useUpdateChallenge(challenge.id);
  const [selectedCluster, setSelectedCluster] = useState("");
  const [rowError, setRowError] = useState<string | null>(null);

  async function handleAssign() {
    if (!selectedCluster) return;
    setRowError(null);
    try {
      await updateChallenge.mutateAsync({ cluster_id: selectedCluster });
    } catch (err) {
      setRowError(errorMessage(err));
    }
  }

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-medium text-slate-900">{challenge.title}</p>
          <p className="mt-1 text-sm text-slate-500">{challenge.description}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <StatusBadge status={challenge.status} />
          {challenge.severity ? <StatusBadge status={challenge.severity} /> : null}
        </div>
      </div>
      <p className="text-xs text-slate-400">Submitted {new Date(challenge.created_at).toLocaleString()}</p>

      {canCluster ? (
        <div className="flex items-center gap-2 border-t border-slate-100 pt-3">
          <Select
            aria-label={`Assign ${challenge.title} to a cluster`}
            value={selectedCluster}
            onChange={(e) => setSelectedCluster(e.target.value)}
            disabled={clustersQuery.isLoading || updateChallenge.isPending}
          >
            <option value="" disabled>
              {clustersQuery.isLoading ? "Loading clusters…" : "Assign to cluster…"}
            </option>
            {(clustersQuery.data?.items ?? []).map((cluster) => (
              <option key={cluster.id} value={cluster.id}>
                {cluster.title}
              </option>
            ))}
          </Select>
          <Button onClick={() => void handleAssign()} disabled={!selectedCluster || updateChallenge.isPending}>
            {updateChallenge.isPending ? "Assigning…" : "Assign"}
          </Button>
          {rowError ? <span className="text-sm text-red-600">{rowError}</span> : null}
        </div>
      ) : null}
    </Card>
  );
}

export default function PendingTriagePage() {
  const { user } = useAuth();
  const canCluster = user ? canManageClustersThemes(user.role) : false;

  const pagination = useCursorPagination<ChallengeResponse>();
  const query = useChallengesList({ unclustered: true, cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);

  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  return (
    <div>
      <PageHeader
        title="Pending Triage"
        description="Newly submitted challenges with no cluster assigned yet: the step that makes a challenge visible to University/Industry once it becomes a project."
      />

      {showInitialLoading ? (
        <Spinner label="Loading pending challenges…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="Nothing pending triage" description="Every submitted challenge has been assigned to a cluster." />
      ) : (
        <div className="flex flex-col gap-3">
          {pagination.items.map((challenge) => (
            <TriageRow key={challenge.id} challenge={challenge} canCluster={canCluster} />
          ))}
        </div>
      )}

      {pagination.hasNext ? (
        <div className="mt-4 flex justify-center">
          <Button variant="secondary" onClick={pagination.loadMore} disabled={query.isFetching}>
            {query.isFetching ? "Loading…" : "Load more"}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
