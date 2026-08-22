"use client";

import Link from "next/link";
import { useState } from "react";
import { useSearchParams } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import { useChallengesList } from "@/hooks/useChallengeQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, type Column } from "@/components/ui/Table";
import type { ChallengeResponse, ChallengeStatus } from "@/types/api";

const STATUSES: ChallengeStatus[] = ["submitted", "open", "duplicate", "resolved"];

export default function ChallengesPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const mineOnly = searchParams.get("mine") === "true";
  const [status, setStatus] = useState<ChallengeStatus | undefined>(undefined);

  const pagination = useCursorPagination<ChallengeResponse>();
  const query = useChallengesList({ status, cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);

  // No owner filter exists server-side for citizen-authored challenges; a
  // Field Assistant's "my assisted cases" is filtered client-side against
  // the already-returned submitted_by_id (their own user id), not invented
  // as a backend query param.
  const challenges = mineOnly ? pagination.items.filter((c) => c.submitted_by_id === user?.id) : pagination.items;

  const columns: Column<ChallengeResponse>[] = [
    { key: "title", header: "Title", render: (c) => c.title },
    { key: "status", header: "Status", render: (c) => <StatusBadge status={c.status} /> },
    {
      key: "severity",
      header: "Severity",
      render: (c) => (c.severity ? <StatusBadge status={c.severity} /> : <span className="text-slate-400">—</span>),
    },
    { key: "updated", header: "Last updated", render: (c) => new Date(c.updated_at).toLocaleDateString() },
    {
      key: "details",
      header: "",
      render: (c) => (
        <Link href={`/organization/government/challenges/${c.id}`} className="font-medium text-slate-600 hover:underline">
          View →
        </Link>
      ),
    },
  ];

  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  return (
    <div>
      <PageHeader
        title={mineOnly ? "My Assisted Cases" : "Challenges"}
        actions={
          <Select
            aria-label="Filter by status"
            value={status ?? ""}
            onChange={(e) => {
              setStatus((e.target.value || undefined) as ChallengeStatus | undefined);
              pagination.reset();
            }}
          >
            <option value="">All statuses</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
        }
      />

      {showInitialLoading ? (
        <Spinner label="Loading challenges…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : challenges.length === 0 ? (
        <EmptyState title="No challenges found" />
      ) : (
        <Table columns={columns} rows={challenges} />
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
