"use client";

import { useState } from "react";

import { useConfirmConsortium, useConsortiumMembers, useProjectConsortium, useRequestConsortium } from "@/hooks/useConsortium";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Spinner } from "@/components/ui/Spinner";
import { Table, type Column } from "@/components/ui/Table";
import type { ConsortiumMemberResponse } from "@/types/api";

/** ML suggests a team composition (see rationale/match_score per member) —
 * a Coordinator/Faculty confirmation is the authoritative decision that
 * activates the consortium. The AI never forms a team on its own. */
export function ConsortiumPanel({ projectId }: { projectId: string }) {
  const consortiumQuery = useProjectConsortium(projectId);
  const requestConsortium = useRequestConsortium(projectId);
  const confirmConsortium = useConfirmConsortium(projectId);
  const [actionError, setActionError] = useState<string | null>(null);

  const consortium = consortiumQuery.data ?? null;
  const membersQuery = useConsortiumMembers(consortium?.id);

  async function handleRequest() {
    setActionError(null);
    try {
      await requestConsortium.mutateAsync(3);
    } catch (err) {
      setActionError(errorMessage(err));
    }
  }

  async function handleConfirm() {
    if (!consortium) return;
    setActionError(null);
    try {
      await confirmConsortium.mutateAsync(consortium.id);
    } catch (err) {
      setActionError(errorMessage(err));
    }
  }

  if (consortiumQuery.isLoading) {
    return <Spinner label="Loading consortium…" />;
  }

  if (consortiumQuery.isError) {
    return <ErrorState error={consortiumQuery.error} onRetry={() => consortiumQuery.refetch()} />;
  }

  const columns: Column<ConsortiumMemberResponse>[] = [
    { key: "organization", header: "Organization", render: (m) => m.organization_id },
    { key: "role", header: "Role", render: (m) => m.role },
    {
      key: "score",
      header: "Match score",
      render: (m) => (m.match_score != null ? m.match_score.toFixed(2) : "—"),
    },
    { key: "rationale", header: "Rationale", render: (m) => m.rationale ?? "—" },
  ];

  return (
    <div>
      {!consortium ? (
        <EmptyState
          title="No consortium yet"
          description="Ask the ML matching engine to suggest a complementary team of organizations for this project. You confirm the final team — the suggestion is never automatic."
          action={
            <Button onClick={() => void handleRequest()} disabled={requestConsortium.isPending}>
              {requestConsortium.isPending ? "Requesting…" : "Request consortium suggestion"}
            </Button>
          }
        />
      ) : (
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-700">
                Consortium — {consortium.status === "confirmed" ? "Confirmed" : "Proposed (awaiting confirmation)"}
              </h2>
              <p className="text-xs text-slate-500">Created {new Date(consortium.created_at).toLocaleDateString()}</p>
            </div>
            {consortium.status === "proposed" ? (
              <Button onClick={() => void handleConfirm()} disabled={confirmConsortium.isPending}>
                {confirmConsortium.isPending ? "Confirming…" : "Confirm consortium"}
              </Button>
            ) : null}
          </div>

          {membersQuery.isLoading ? (
            <Spinner />
          ) : membersQuery.isError ? (
            <ErrorState error={membersQuery.error} onRetry={() => membersQuery.refetch()} />
          ) : (membersQuery.data ?? []).length === 0 ? (
            <p className="text-sm text-slate-500">
              Suggestion queued — this runs in the background and members will appear here shortly. Refresh to check.
            </p>
          ) : (
            <Table columns={columns} rows={membersQuery.data ?? []} />
          )}
        </Card>
      )}
      {actionError ? (
        <p role="alert" className="mt-2 text-sm text-red-600">
          {actionError}
        </p>
      ) : null}
    </div>
  );
}
