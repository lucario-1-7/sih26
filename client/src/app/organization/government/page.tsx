"use client";

import Link from "next/link";

import { useAuth } from "@/hooks/useAuth";
import { useChallengesList } from "@/hooks/useChallengeQueries";
import { useClustersList } from "@/hooks/useThemeClusterQueries";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ChallengeResponse, ChallengeStatus } from "@/types/api";

function countByStatus(challenges: ChallengeResponse[], status: ChallengeStatus): number {
  return challenges.filter((c) => c.status === status).length;
}

export default function GovernmentDashboardPage() {
  const { user } = useAuth();
  const isValidator = user?.role === "validator";

  const challengesQuery = useChallengesList({});
  const clustersQuery = useClustersList({ status: "active" });
  const challenges = challengesQuery.data?.items ?? [];

  return (
    <div>
      <PageHeader
        title={isValidator ? "Validator Dashboard" : "Field Assistant Dashboard"}
        description={
          isValidator
            ? "Challenge review, duplicate detection, and severity workflow."
            : "Assisted citizen submissions and case tracking."
        }
      />

      {challengesQuery.isLoading ? (
        <Spinner label="Loading summary…" />
      ) : challengesQuery.isError ? (
        <ErrorState error={challengesQuery.error} onRetry={() => challengesQuery.refetch()} />
      ) : (
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Submitted" value={countByStatus(challenges, "submitted")} />
          <StatCard label="Open" value={countByStatus(challenges, "open")} />
          <StatCard label="Flagged Duplicate" value={countByStatus(challenges, "duplicate")} />
          <StatCard label="Resolved" value={countByStatus(challenges, "resolved")} />
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900">Recent challenges</h2>
            <Link href="/organization/government/challenges" className="text-sm font-medium text-slate-600 hover:underline">
              View all
            </Link>
          </div>
          {challengesQuery.isLoading ? (
            <Spinner />
          ) : challenges.length === 0 ? (
            <p className="text-sm text-slate-500">No challenges yet.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {challenges.slice(0, 5).map((challenge) => (
                <li key={challenge.id} className="flex items-center justify-between text-sm">
                  <Link
                    href={`/organization/government/challenges/${challenge.id}`}
                    className="font-medium text-slate-900 hover:underline"
                  >
                    {challenge.title}
                  </Link>
                  <StatusBadge status={challenge.status} />
                </li>
              ))}
            </ul>
          )}
        </Card>

        {isValidator ? (
          <Card>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-900">Active clusters</h2>
              <Link href="/organization/government/clusters" className="text-sm font-medium text-slate-600 hover:underline">
                View all
              </Link>
            </div>
            {clustersQuery.isLoading ? (
              <Spinner />
            ) : clustersQuery.isError ? (
              <ErrorState error={clustersQuery.error} onRetry={() => clustersQuery.refetch()} />
            ) : (clustersQuery.data?.items.length ?? 0) === 0 ? (
              <p className="text-sm text-slate-500">No active clusters.</p>
            ) : (
              <ul className="flex flex-col gap-3">
                {clustersQuery.data!.items.slice(0, 5).map((cluster) => (
                  <li key={cluster.id} className="text-sm font-medium text-slate-900">
                    {cluster.title}
                  </li>
                ))}
              </ul>
            )}
          </Card>
        ) : (
          <Card>
            <h2 className="mb-3 text-base font-semibold text-slate-900">Submit for a citizen</h2>
            <p className="mb-3 text-sm text-slate-500">
              Capture a challenge on behalf of a citizen who doesn&apos;t have — or isn&apos;t using — the app.
            </p>
            <Link
              href="/organization/government/assisted-submission"
              className="text-sm font-medium text-slate-900 underline"
            >
              Start assisted submission →
            </Link>
          </Card>
        )}
      </div>
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
