"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useCreateMilestone, useMilestonesList, useUpdateMilestone } from "@/hooks/useProjectQueries";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, type Column } from "@/components/ui/Table";
import type { MilestoneResponse, MilestoneStatus } from "@/types/api";

const MILESTONE_STATUSES: MilestoneStatus[] = ["pending", "in_progress", "completed", "blocked"];

export function MilestonesPanel({ projectId }: { projectId: string }) {
  const query = useMilestonesList(projectId);
  const createMilestone = useCreateMilestone(projectId);
  const updateMilestone = useUpdateMilestone(projectId);

  const [modalOpen, setModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  const milestones = [...(query.data?.items ?? [])].sort((a, b) => a.order - b.order);
  const total = milestones.length;
  const completed = milestones.filter((m) => m.status === "completed").length;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const title = String(form.get("title") ?? "").trim();
    const description = String(form.get("description") ?? "").trim() || null;
    const due_date = String(form.get("due_date") ?? "").trim() || null;
    const order = Number(form.get("order") ?? 0);

    setFormError(null);
    try {
      await createMilestone.mutateAsync({ title, description, due_date, order });
      setModalOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  async function handleStatusChange(milestone: MilestoneResponse, status: MilestoneStatus) {
    setStatusError(null);
    try {
      await updateMilestone.mutateAsync({ milestoneId: milestone.id, data: { status } });
    } catch (err) {
      setStatusError(errorMessage(err));
    }
  }

  const columns: Column<MilestoneResponse>[] = [
    { key: "title", header: "Title", render: (m) => m.title },
    { key: "due_date", header: "Due date", render: (m) => (m.due_date ? new Date(m.due_date).toLocaleDateString() : "—") },
    {
      key: "status",
      header: "Status",
      render: (m) => (
        <div className="flex items-center gap-2">
          <StatusBadge status={m.status} />
          <label className="sr-only" htmlFor={`milestone-status-${m.id}`}>
            Change status for {m.title}
          </label>
          <Select
            id={`milestone-status-${m.id}`}
            value={m.status}
            onChange={(e) => void handleStatusChange(m, e.target.value as MilestoneStatus)}
          >
            {MILESTONE_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
        </div>
      ),
    },
    {
      key: "completed_at",
      header: "Completed",
      render: (m) => (m.completed_at ? new Date(m.completed_at).toLocaleDateString() : "—"),
    },
  ];

  return (
    <div>
      {total > 0 ? (
        <p className="mb-3 text-sm text-slate-500">
          {completed} of {total} milestones completed
        </p>
      ) : null}

      <div className="mb-3 flex justify-end">
        <Button onClick={() => setModalOpen(true)}>New milestone</Button>
      </div>

      {statusError ? (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {statusError}
        </p>
      ) : null}

      {query.isLoading ? (
        <Spinner />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : milestones.length === 0 ? (
        <EmptyState title="No milestones yet" />
      ) : (
        <Table columns={columns} rows={milestones} />
      )}

      <Modal open={modalOpen} title="New milestone" onClose={() => setModalOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Title" htmlFor="title">
            <Input id="title" name="title" required minLength={3} />
          </Field>
          <Field label="Description" htmlFor="description">
            <Input id="description" name="description" />
          </Field>
          <Field label="Due date" htmlFor="due_date">
            <Input id="due_date" name="due_date" type="date" />
          </Field>
          <Field label="Order" htmlFor="order">
            <Input id="order" name="order" type="number" min={0} defaultValue={0} />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createMilestone.isPending}>
            Create milestone
          </Button>
        </form>
      </Modal>
    </div>
  );
}
