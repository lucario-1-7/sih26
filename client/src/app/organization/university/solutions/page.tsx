"use client";

import Link from "next/link";

import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { useSolutionsList } from "@/hooks/useSolutionQueries";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { SolutionResponse } from "@/types/api";

export default function SolutionsPage() {
  const pagination = useCursorPagination<SolutionResponse>();
  const query = useSolutionsList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);

  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  return (
    <div>
      <PageHeader title="Solutions" description="Outcomes registered from completed projects." />

      {showInitialLoading ? (
        <Spinner label="Loading solutions…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No solutions registered yet" />
      ) : (
        <div className="flex flex-col gap-3">
          {pagination.items.map((solution) => (
            <Card key={solution.id}>
              <div className="flex items-center justify-between">
                <Link href={`/organization/university/solutions/${solution.id}`} className="font-medium text-slate-900 hover:underline">
                  {solution.title}
                </Link>
                <StatusBadge status={solution.status} />
              </div>
              {solution.outcome ? <p className="mt-2 text-sm text-slate-600">{solution.outcome}</p> : null}
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
