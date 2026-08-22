"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useClustersList, useCreateCluster } from "@/hooks/useThemeClusterQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { canManageClustersThemes } from "@/lib/rbac/config";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ClusterResponse } from "@/types/api";

export default function ClustersPage() {
  const { user } = useAuth();
  const pagination = useCursorPagination<ClusterResponse>();
  const query = useClustersList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);
  const createCluster = useCreateCluster();

  const [createOpen, setCreateOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const canManage = user ? canManageClustersThemes(user.role) : false;
  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const title = String(form.get("title") ?? "").trim();
    const description = String(form.get("description") ?? "").trim() || null;

    setFormError(null);
    try {
      await createCluster.mutateAsync({ title, description });
      setCreateOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader
        title="Clusters"
        description="Systemic-problem groupings — the unit projects execute against."
        actions={canManage ? <Button onClick={() => setCreateOpen(true)}>New cluster</Button> : undefined}
      />

      {showInitialLoading ? (
        <Spinner label="Loading clusters…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No clusters yet" />
      ) : (
        <div className="flex flex-col gap-3">
          {pagination.items.map((cluster) => (
            <Card key={cluster.id} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">{cluster.title}</p>
                {cluster.description ? <p className="mt-1 text-sm text-slate-500">{cluster.description}</p> : null}
              </div>
              <StatusBadge status={cluster.status} />
            </Card>
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

      <Modal open={createOpen} title="New cluster" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Title" htmlFor="c-title">
            <Input id="c-title" name="title" required minLength={3} />
          </Field>
          <Field label="Description" htmlFor="c-description">
            <Input id="c-description" name="description" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createCluster.isPending}>
            Create cluster
          </Button>
        </form>
      </Modal>
    </div>
  );
}
