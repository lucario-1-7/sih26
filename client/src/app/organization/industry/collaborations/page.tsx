"use client";

import Link from "next/link";

import { useCollaborationsList } from "@/hooks/useCollaborationQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, type Column } from "@/components/ui/Table";
import type { CollaborationResponse } from "@/types/api";

export default function CollaborationsPage() {
  const pagination = useCursorPagination<CollaborationResponse>();
  const query = useCollaborationsList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);
  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  const columns: Column<CollaborationResponse>[] = [
    { key: "project", header: "Project", render: (c) => <code className="font-mono text-xs">{c.project_id}</code> },
    { key: "type", header: "Type", render: (c) => c.type.replace(/_/g, " ") },
    { key: "status", header: "Status", render: (c) => <StatusBadge status={c.status} /> },
    { key: "updated", header: "Last updated", render: (c) => new Date(c.updated_at).toLocaleDateString() },
    {
      key: "details",
      header: "",
      render: (c) => (
        <Link href={`/organization/industry/collaborations/${c.id}`} className="font-medium text-slate-600 hover:underline">
          View →
        </Link>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="Collaborations" description="Your organization's collaboration lifecycle." />

      {showInitialLoading ? (
        <Spinner label="Loading collaborations…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No collaborations yet" />
      ) : (
        <Table columns={columns} rows={pagination.items} />
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
