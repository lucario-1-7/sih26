"use client";

import Link from "next/link";

import { useProjectsList } from "@/hooks/useProjectQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { UniversityUptakeInline } from "@/components/organization/UniversityUptake";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, type Column } from "@/components/ui/Table";
import type { ProjectResponse } from "@/types/api";

export default function GovernmentProjectsPage() {
  const pagination = useCursorPagination<ProjectResponse>();
  const query = useProjectsList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);
  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  const columns: Column<ProjectResponse>[] = [
    { key: "title", header: "Title", render: (p) => p.title },
    { key: "status", header: "Status", render: (p) => <StatusBadge status={p.status} /> },
    {
      key: "university",
      header: "Taken up by",
      render: (p) => <UniversityUptakeInline university={p.university} />,
    },
    { key: "updated", header: "Last updated", render: (p) => new Date(p.updated_at).toLocaleDateString() },
    {
      key: "details",
      header: "",
      render: (p) => (
        <Link href={`/organization/government/projects/${p.id}`} className="font-medium text-slate-600 hover:underline">
          View →
        </Link>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="Projects" description="Read-only visibility for government review — impact verification available where applicable." />

      {showInitialLoading ? (
        <Spinner label="Loading projects…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No projects found" />
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
