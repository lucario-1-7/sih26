"use client";

import { useState } from "react";

import { useUpdateCollaborationStatus } from "@/hooks/useCollaborationQueries";
import { Button } from "@/components/ui/Button";
import { errorMessage } from "@/components/ui/ErrorState";
import { COLLABORATION_STATUS_TRANSITIONS } from "@/types/api";
import type { CollaborationResponse, CollaborationStatus } from "@/types/api";

const ACTION_LABEL: Record<CollaborationStatus, string> = {
  interested: "Mark interested",
  proposed: "Submit proposal",
  accepted: "Accept",
  active: "Activate",
  completed: "Mark completed",
  rejected: "Reject",
};

/** Industry proposes (interested->proposed) — university/superadmin accept,
 * activate, complete, or reject. The backend enforces which side may
 * perform which transition; a button that's the wrong side for the current
 * user will simply 403 — shown via `errorMessage`, not hidden silently,
 * since the frontend can't always know the caller's exact authorized side
 * without duplicating backend logic. */
export function CollaborationStatusActions({ collaboration }: { collaboration: CollaborationResponse }) {
  const updateStatus = useUpdateCollaborationStatus(collaboration.id);
  const [error, setError] = useState<string | null>(null);
  const nextStates = COLLABORATION_STATUS_TRANSITIONS[collaboration.status];

  async function transition(status: CollaborationStatus) {
    setError(null);
    try {
      await updateStatus.mutateAsync({ status });
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  if (nextStates.length === 0) {
    return <p className="text-sm text-slate-500">This collaboration is in a final state.</p>;
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {nextStates.map((status) => (
          <Button
            key={status}
            variant={status === "rejected" ? "danger" : "secondary"}
            onClick={() => void transition(status)}
            disabled={updateStatus.isPending}
          >
            {ACTION_LABEL[status]}
          </Button>
        ))}
      </div>
      {error ? (
        <p role="alert" className="mt-2 text-sm text-red-600">
          {error}
        </p>
      ) : null}
    </div>
  );
}
