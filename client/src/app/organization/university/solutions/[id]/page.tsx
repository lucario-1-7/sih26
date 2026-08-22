"use client";

import { useState } from "react";
import { useParams } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import { useReplicationCandidates, useSolution, useUpdateSolution } from "@/hooks/useSolutionQueries";
import { canPublishSolution } from "@/lib/rbac/config";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function SolutionDetailsPage() {
  const { user } = useAuth();
  const params = useParams<{ id: string }>();
  const solutionId = params.id;

  const query = useSolution(solutionId);
  const updateSolution = useUpdateSolution(solutionId);
  const replicationQuery = useReplicationCandidates(solutionId);
  const [publishError, setPublishError] = useState<string | null>(null);

  if (query.isLoading) {
    return (
      <div className="flex justify-center p-12">
        <Spinner label="Loading solution…" />
      </div>
    );
  }
  if (query.isError || !query.data) {
    return <ErrorState error={query.error} onRetry={() => query.refetch()} />;
  }

  const solution = query.data;
  const candidates = replicationQuery.data ?? [];

  async function handlePublish() {
    setPublishError(null);
    try {
      await updateSolution.mutateAsync({ status: "published" });
    } catch (err) {
      setPublishError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader title={solution.title} actions={<StatusBadge status={solution.status} />} />

      <Card className="mb-6">
        <h2 className="mb-2 text-sm font-semibold text-slate-700">Outcome</h2>
        <p className="text-sm text-slate-700">{solution.outcome ?? "No outcome recorded yet."}</p>

        {solution.status === "draft" && user && canPublishSolution(user.role) ? (
          <div className="mt-4">
            <Button onClick={() => void handlePublish()} disabled={updateSolution.isPending}>
              Publish solution
            </Button>
            {publishError ? (
              <p role="alert" className="mt-2 text-sm text-red-600">
                {publishError}
              </p>
            ) : null}
          </div>
        ) : null}
      </Card>

      <Card>
        <h2 className="mb-1 text-sm font-semibold text-slate-700">Recommended Replication Candidates</h2>
        <p className="mb-3 text-xs text-slate-500">
          Ranked by similarity to open clusters with no project yet. This is a recommendation only — replication
          requires a Coordinator to review and propose a project; nothing here happens automatically.
        </p>

        {replicationQuery.isLoading ? (
          <Spinner />
        ) : replicationQuery.isError ? (
          <ErrorState error={replicationQuery.error} onRetry={() => replicationQuery.refetch()} />
        ) : candidates.length === 0 ? (
          <EmptyState title="No replication candidates found" />
        ) : (
          <ul className="flex flex-col gap-2">
            {candidates.map((c) => (
              <li key={c.cluster_id} className="flex items-center justify-between text-sm">
                <span className="text-slate-800">{c.cluster_title}</span>
                <Badge tone="info">{Math.round(c.similarity * 100)}% similar</Badge>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
