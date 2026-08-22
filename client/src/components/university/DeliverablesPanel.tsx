"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import {
  useCreateDeliverable,
  useDeliverablesList,
  useUpdateDeliverable,
  useVerifyDeliverable,
} from "@/hooks/useProjectQueries";
import { useAuth } from "@/hooks/useAuth";
import { canVerifyDeliverable } from "@/lib/rbac/config";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input, Textarea } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, type Column } from "@/components/ui/Table";
import type { DeliverableResponse } from "@/types/api";

export function DeliverablesPanel({ projectId }: { projectId: string }) {
  const { user } = useAuth();
  const query = useDeliverablesList(projectId);
  const createDeliverable = useCreateDeliverable(projectId);
  const updateDeliverable = useUpdateDeliverable(projectId);
  const verifyDeliverable = useVerifyDeliverable(projectId);

  const [createOpen, setCreateOpen] = useState(false);
  const [submitTarget, setSubmitTarget] = useState<DeliverableResponse | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const deliverables = query.data?.items ?? [];
  const canVerify = user ? canVerifyDeliverable(user.role) : false;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const title = String(form.get("title") ?? "").trim();
    const description = String(form.get("description") ?? "").trim() || null;
    const due_date = String(form.get("due_date") ?? "").trim() || null;

    setFormError(null);
    try {
      await createDeliverable.mutateAsync({ title, description, due_date });
      setCreateOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  async function handleSubmitEvidence(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!submitTarget) return;
    const form = new FormData(e.currentTarget);
    const evidence = String(form.get("evidence") ?? "").trim();

    setFormError(null);
    try {
      await updateDeliverable.mutateAsync({ deliverableId: submitTarget.id, data: { evidence } });
      setSubmitTarget(null);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  async function handleVerify(deliverable: DeliverableResponse, approve: boolean) {
    setActionError(null);
    try {
      await verifyDeliverable.mutateAsync({ deliverableId: deliverable.id, approve });
    } catch (err) {
      setActionError(errorMessage(err));
    }
  }

  const columns: Column<DeliverableResponse>[] = [
    { key: "title", header: "Title", render: (d) => d.title },
    { key: "due_date", header: "Due date", render: (d) => (d.due_date ? new Date(d.due_date).toLocaleDateString() : "—") },
    { key: "status", header: "Status", render: (d) => <StatusBadge status={d.status} /> },
    {
      key: "actions",
      header: "",
      render: (d) => (
        <div className="flex gap-2">
          {d.status === "pending" || d.status === "rejected" ? (
            <Button variant="secondary" onClick={() => setSubmitTarget(d)}>
              Submit evidence
            </Button>
          ) : null}
          {canVerify && d.status === "submitted" ? (
            <>
              <Button variant="secondary" onClick={() => void handleVerify(d, true)}>
                Verify
              </Button>
              <Button variant="danger" onClick={() => void handleVerify(d, false)}>
                Reject
              </Button>
            </>
          ) : null}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="mb-3 flex justify-end">
        <Button onClick={() => setCreateOpen(true)}>New deliverable</Button>
      </div>

      {actionError ? (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {actionError}
        </p>
      ) : null}

      {query.isLoading ? (
        <Spinner />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : deliverables.length === 0 ? (
        <EmptyState title="No deliverables yet" />
      ) : (
        <Table columns={columns} rows={deliverables} />
      )}

      <Modal open={createOpen} title="New deliverable" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Title" htmlFor="d-title">
            <Input id="d-title" name="title" required minLength={3} />
          </Field>
          <Field label="Description" htmlFor="d-description">
            <Textarea id="d-description" name="description" rows={3} />
          </Field>
          <Field label="Due date" htmlFor="d-due_date">
            <Input id="d-due_date" name="due_date" type="date" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createDeliverable.isPending}>
            Create deliverable
          </Button>
        </form>
      </Modal>

      <Modal open={submitTarget !== null} title="Submit evidence" onClose={() => setSubmitTarget(null)}>
        <form onSubmit={handleSubmitEvidence} className="flex flex-col gap-4">
          <Field label="Evidence (link or description)" htmlFor="evidence">
            <Textarea id="evidence" name="evidence" rows={4} required defaultValue={submitTarget?.evidence ?? ""} />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={updateDeliverable.isPending}>
            Submit for verification
          </Button>
        </form>
      </Modal>
    </div>
  );
}
