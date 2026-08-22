"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { useAuth } from "@/hooks/useAuth";
import { useProjectsList } from "@/hooks/useProjectQueries";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, type Column } from "@/components/ui/Table";
import type { ProjectResponse } from "@/types/api";

export default function ProjectsPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const mineOnly = searchParams.get("mine") === "true";

  const pagination = useCursorPagination<ProjectResponse>();
  const query = useProjectsList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);

  // The backend's list endpoint filters by cluster/status only — there is no
  // owner filter param, so "My Projects" is applied client-side against the
  // already-returned owner_id rather than inventing a backend query param.
  const projects = mineOnly ? pagination.items.filter((p) => p.owner_id === user?.id) : pagination.items;
  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  const columns: Column<ProjectResponse>[] = [
    { key: "title", header: "Title", render: (p) => p.title },
    { key: "status", header: "Status", render: (p) => <StatusBadge status={p.status} /> },
    {
      key: "updated_at",
      header: "Last updated",
      render: (p) => new Date(p.updated_at).toLocaleDateString(),
    },
    {
      key: "details",
      header: "",
      render: (p) => (
        <Link href={`/organization/university/projects/${p.id}`} className="font-medium text-slate-600 hover:underline">
          View details →
        </Link>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title={mineOnly ? "My Projects" : "Projects"} description="Projects visible to your institution." />

      {showInitialLoading ? (
        <Spinner label="Loading projects…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : projects.length === 0 ? (
        <EmptyState title="No projects found" />
      ) : (
        <Table columns={columns} rows={projects} />
      )}

      {pagination.hasNext && projects.length > 0 ? (
        <div className="mt-4 flex justify-center">
          <Button variant="secondary" onClick={pagination.loadMore} disabled={query.isFetching}>
            {query.isFetching ? "Loading…" : "Load more"}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
