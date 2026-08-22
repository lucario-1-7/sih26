"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useCommitmentsList, useCreateCommitment, useUpdateCommitmentStatus } from "@/hooks/useCollaborationQueries";
import { canCreateCommitment, canReviewCommitment } from "@/lib/rbac/config";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { CollaborationType, CommitmentResponse } from "@/types/api";

const TYPES: CollaborationType[] = ["funding", "mentoring", "equipment", "technical_support", "pilot_support", "other"];

export function CommitmentsPanel({ collaborationId }: { collaborationId: string }) {
  const { user } = useAuth();
  const query = useCommitmentsList(collaborationId);
  const createCommitment = useCreateCommitment(collaborationId);
  const updateStatus = useUpdateCommitmentStatus(collaborationId);

  const [createOpen, setCreateOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const commitments = query.data?.items ?? [];
  const canCreate = user ? canCreateCommitment(user.role) : false;
  const canReview = user ? canReviewCommitment(user.role) : false;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const type = String(form.get("type") ?? "") as CollaborationType;
    const amount = form.get("amount") ? Number(form.get("amount")) : null;
    const currency = String(form.get("currency") ?? "").trim() || null;
    const description = String(form.get("description") ?? "").trim() || null;

    setFormError(null);
    try {
      await createCommitment.mutateAsync({ type, amount, currency, description });
      setCreateOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  async function handleReview(commitment: CommitmentResponse, status: "accepted" | "fulfilled" | "rejected") {
    setActionError(null);
    try {
      await updateStatus.mutateAsync({ commitmentId: commitment.id, data: { status } });
    } catch (err) {
      setActionError(errorMessage(err));
    }
  }

  if (query.isLoading) return <Spinner />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  return (
    <div>
      {canCreate ? (
        <div className="mb-3 flex justify-end">
          <Button onClick={() => setCreateOpen(true)}>Propose commitment</Button>
        </div>
      ) : null}

      {actionError ? (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {actionError}
        </p>
      ) : null}

      {commitments.length === 0 ? (
        <EmptyState title="No commitments yet" />
      ) : (
        <div className="flex flex-col gap-3">
          {commitments.map((commitment) => (
            <div key={commitment.id} className="rounded-lg border border-slate-200 p-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="font-medium text-slate-900">{commitment.type.replace(/_/g, " ")}</p>
                <StatusBadge status={commitment.status} />
              </div>
              {commitment.amount !== null ? (
                <p className="font-mono text-sm text-slate-700">
                  {commitment.amount} {commitment.currency ?? ""}
                </p>
              ) : null}
              {commitment.description ? <p className="mt-1 text-sm text-slate-600">{commitment.description}</p> : null}

              {canReview && commitment.status === "proposed" ? (
                <div className="mt-3 flex gap-2">
                  <Button variant="secondary" onClick={() => void handleReview(commitment, "accepted")}>
                    Accept
                  </Button>
                  <Button variant="ghost" onClick={() => void handleReview(commitment, "rejected")}>
                    Reject
                  </Button>
                </div>
              ) : null}
              {canReview && commitment.status === "accepted" ? (
                <div className="mt-3">
                  <Button variant="secondary" onClick={() => void handleReview(commitment, "fulfilled")}>
                    Mark fulfilled
                  </Button>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}

      <Modal open={createOpen} title="Propose commitment" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1 text-sm font-medium text-slate-700" htmlFor="commit-type">
            Type
            <Select id="commit-type" name="type" required defaultValue="">
              <option value="" disabled>
                Select a type…
              </option>
              {TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, " ")}
                </option>
              ))}
            </Select>
          </label>
          <Field label="Amount (optional)" htmlFor="commit-amount">
            <Input id="commit-amount" name="amount" type="number" min={0} step="any" />
          </Field>
          <Field label="Currency (ISO code, optional)" htmlFor="commit-currency">
            <Input id="commit-currency" name="currency" maxLength={3} minLength={3} placeholder="INR" />
          </Field>
          <Field label="Description" htmlFor="commit-description">
            <Input id="commit-description" name="description" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createCommitment.isPending}>
            Propose commitment
          </Button>
        </form>
      </Modal>
    </div>
  );
}
