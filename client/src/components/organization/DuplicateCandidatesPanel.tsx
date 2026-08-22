"use client";

import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useCreateDuplicateDecision, useDuplicateCandidates } from "@/hooks/useChallengeQueries";
import { canMakeDuplicateDecision } from "@/lib/rbac/config";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Spinner } from "@/components/ui/Spinner";
import type { ChallengeResponse } from "@/types/api";

/**
 * Human-in-the-loop duplicate review. The backend never auto-merges or
 * auto-declares a duplicate — candidates are ML evidence only, and every
 * decision here is an explicit, append-only human action (see
 * server/app/services/duplicate_service.py). A second decision on the same
 * pair is a correction, not an error — the original record is preserved,
 * never mutated or deleted.
 */
export function DuplicateCandidatesPanel({ challenge }: { challenge: ChallengeResponse }) {
  const { user } = useAuth();
  const query = useDuplicateCandidates(challenge.id);
  const createDecision = useCreateDuplicateDecision(challenge.id);
  const [decidingFor, setDecidingFor] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const canDecide = user ? canMakeDuplicateDecision(user.role) : false;
  const candidates = query.data ?? [];

  async function decide(candidateChallengeId: string, decision: "duplicate" | "not_duplicate") {
    setDecidingFor(candidateChallengeId);
    setActionError(null);
    try {
      await createDecision.mutateAsync({
        challenge_id: challenge.id,
        candidate_challenge_id: candidateChallengeId,
        decision,
      });
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setDecidingFor(null);
    }
  }

  if (query.isLoading) return <Spinner />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  return (
    <div>
      {challenge.status === "duplicate" && challenge.duplicate_of_id ? (
        <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          Current effective decision: marked as a duplicate of challenge{" "}
          <code className="font-mono">{challenge.duplicate_of_id}</code>. A Validator can still correct this — the
          decision history is append-only and reversible.
        </div>
      ) : null}

      {actionError ? (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {actionError}
        </p>
      ) : null}

      {candidates.length === 0 ? (
        <EmptyState title="No duplicate candidates" description="No similar challenges have been flagged by the ML pipeline." />
      ) : (
        <div className="flex flex-col gap-3">
          <p className="text-xs uppercase tracking-wide text-slate-400">
            Recommendation / evidence — not an automatic determination
          </p>
          {candidates.map((candidate) => (
            <div key={candidate.id} className="rounded-lg border border-slate-200 p-4">
              <div className="mb-2 flex items-center justify-between">
                <code className="font-mono text-sm text-slate-700">{candidate.candidate_challenge_id}</code>
                <Badge tone="info">{Math.round(candidate.similarity_score * 100)}% similarity</Badge>
              </div>
              <p className="mb-3 font-mono text-xs text-slate-400">
                {candidate.model_name} · v{candidate.model_version} · {new Date(candidate.created_at).toLocaleString()}
              </p>
              {canDecide ? (
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    disabled={decidingFor === candidate.candidate_challenge_id}
                    onClick={() => void decide(candidate.candidate_challenge_id, "duplicate")}
                  >
                    Mark duplicate
                  </Button>
                  <Button
                    variant="ghost"
                    disabled={decidingFor === candidate.candidate_challenge_id}
                    onClick={() => void decide(candidate.candidate_challenge_id, "not_duplicate")}
                  >
                    Not a duplicate
                  </Button>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
