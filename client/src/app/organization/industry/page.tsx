"use client";

import Link from "next/link";

import { useCollaborationsList } from "@/hooks/useCollaborationQueries";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { CollaborationResponse, CollaborationStatus } from "@/types/api";

function countByStatus(collaborations: CollaborationResponse[], status: CollaborationStatus): number {
  return collaborations.filter((c) => c.status === status).length;
}

export default function IndustryDashboardPage() {
  const query = useCollaborationsList({});
  const collaborations = query.data?.items ?? [];

  return (
    <div>
      <PageHeader title="Industry Dashboard" description="Your organization's collaborations and commitments." />

      {query.isLoading ? (
        <Spinner label="Loading summary…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : (
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-5">
          <StatCard label="Interested" value={countByStatus(collaborations, "interested")} />
          <StatCard label="Proposed" value={countByStatus(collaborations, "proposed")} />
          <StatCard label="Accepted" value={countByStatus(collaborations, "accepted")} />
          <StatCard label="Active" value={countByStatus(collaborations, "active")} />
          <StatCard label="Completed" value={countByStatus(collaborations, "completed")} />
        </div>
      )}

      <Card>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">Recent collaborations</h2>
          <Link href="/organization/industry/collaborations" className="text-sm font-medium text-slate-600 hover:underline">
            View all
          </Link>
        </div>
        {query.isLoading ? (
          <Spinner />
        ) : collaborations.length === 0 ? (
          <p className="text-sm text-slate-500">
            No collaborations yet.{" "}
            <Link href="/organization/industry/opportunities" className="underline">
              Discover opportunities
            </Link>{" "}
            to get started.
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {collaborations.slice(0, 5).map((collab) => (
              <li key={collab.id} className="flex items-center justify-between text-sm">
                <Link
                  href={`/organization/industry/collaborations/${collab.id}`}
                  className="font-mono font-medium text-slate-900 hover:underline"
                >
                  {collab.project_id}
                </Link>
                <StatusBadge status={collab.status} />
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <p className="text-2xl font-semibold text-slate-900">{value}</p>
      <p className="text-sm text-slate-500">{label}</p>
    </Card>
  );
}
