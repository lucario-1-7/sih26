"use client";

import { useState } from "react";
import { useParams } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import { useChallenge, useUpdateChallenge } from "@/hooks/useChallengeQueries";
import { canSetSeverity } from "@/lib/rbac/config";
import { DuplicateCandidatesPanel } from "@/components/organization/DuplicateCandidatesPanel";
import { Card } from "@/components/ui/Card";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ChallengeSeverity } from "@/types/api";

const SEVERITIES: ChallengeSeverity[] = ["low", "medium", "high", "critical"];

export default function ChallengeDetailsPage() {
  const { user } = useAuth();
  const params = useParams<{ id: string }>();
  const challengeId = params.id;

  const query = useChallenge(challengeId);
  const updateChallenge = useUpdateChallenge(challengeId);
  const [severityError, setSeverityError] = useState<string | null>(null);

  if (query.isLoading) {
    return (
      <div className="flex justify-center p-12">
        <Spinner label="Loading challenge…" />
      </div>
    );
  }
  if (query.isError || !query.data) {
    return <ErrorState error={query.error} onRetry={() => query.refetch()} />;
  }

  const challenge = query.data;
  const canEditSeverity = user ? canSetSeverity(user.role) : false;

  async function handleSeverityChange(severity: ChallengeSeverity) {
    setSeverityError(null);
    try {
      await updateChallenge.mutateAsync({ severity });
    } catch (err) {
      setSeverityError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader title={challenge.title} actions={<StatusBadge status={challenge.status} />} />

      <Card className="mb-6">
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <dt className="text-xs font-medium uppercase text-slate-400">Description</dt>
            <dd className="mt-1 text-sm text-slate-700">{challenge.description}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Cluster</dt>
            <dd className="mt-1 font-mono text-sm text-slate-700">{challenge.cluster_id ?? "Not clustered yet"}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Submitted</dt>
            <dd className="mt-1 text-sm text-slate-700">{new Date(challenge.created_at).toLocaleString()}</dd>
          </div>
          {challenge.on_behalf_of_name ? (
            <div className="sm:col-span-2">
              <dt className="text-xs font-medium uppercase text-slate-400">Assisted submission — on behalf of</dt>
              <dd className="mt-1 text-sm text-slate-700">
                {challenge.on_behalf_of_name}
                {challenge.on_behalf_of_phone ? ` · ${challenge.on_behalf_of_phone}` : ""}
              </dd>
            </div>
          ) : null}
        </dl>

        <div className="mt-4 border-t border-slate-100 pt-4">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Severity</h2>
          {canEditSeverity ? (
            <div className="flex items-center gap-2">
              <Select
                aria-label="Set severity"
                value={challenge.severity ?? ""}
                onChange={(e) => void handleSeverityChange(e.target.value as ChallengeSeverity)}
                disabled={updateChallenge.isPending}
              >
                <option value="" disabled>
                  Set severity…
                </option>
                {SEVERITIES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </Select>
              {severityError ? <span className="text-sm text-red-600">{severityError}</span> : null}
            </div>
          ) : challenge.severity ? (
            <StatusBadge status={challenge.severity} />
          ) : (
            <p className="text-sm text-slate-500">Not yet reviewed.</p>
          )}
        </div>
      </Card>

      <Card>
        <h2 className="mb-3 text-base font-semibold text-slate-900">Duplicate detection</h2>
        <DuplicateCandidatesPanel challenge={challenge} />
      </Card>
    </div>
  );
}
