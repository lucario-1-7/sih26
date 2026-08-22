"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useCreateParticipant, useParticipantsList, useUpdateParticipant } from "@/hooks/useProjectQueries";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Spinner } from "@/components/ui/Spinner";
import { Table, type Column } from "@/components/ui/Table";
import type { ProjectParticipantResponse } from "@/types/api";

export function ParticipantsPanel({ projectId }: { projectId: string }) {
  const query = useParticipantsList(projectId);
  const createParticipant = useCreateParticipant(projectId);
  const updateParticipant = useUpdateParticipant(projectId);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ProjectParticipantResponse | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const participants = query.data?.items ?? [];

  function openCreate() {
    setEditing(null);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(participant: ProjectParticipantResponse) {
    setEditing(participant);
    setFormError(null);
    setModalOpen(true);
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const name = String(form.get("name") ?? "").trim();
    const department = String(form.get("department") ?? "").trim() || null;
    const academic_year = String(form.get("academic_year") ?? "").trim() || null;
    const registration_id = String(form.get("registration_id") ?? "").trim() || null;

    setFormError(null);
    try {
      if (editing) {
        await updateParticipant.mutateAsync({
          participantId: editing.id,
          data: { name, department, academic_year, registration_id },
        });
      } else {
        await createParticipant.mutateAsync({ name, department, academic_year, registration_id });
      }
      setModalOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  const columns: Column<ProjectParticipantResponse>[] = [
    { key: "name", header: "Name", render: (p) => p.name },
    { key: "department", header: "Department", render: (p) => p.department ?? "—" },
    { key: "year", header: "Year", render: (p) => p.academic_year ?? "—" },
    { key: "role", header: "Role", render: (p) => p.participation_role },
    {
      key: "actions",
      header: "",
      render: (p) => (
        <Button variant="ghost" onClick={() => openEdit(p)}>
          Edit
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div className="mb-3 flex justify-between">
        <p className="text-sm text-slate-500">
          Students do not have platform accounts — these are participant records maintained by Faculty/Coordinator.
        </p>
        <Button onClick={openCreate}>Add participant</Button>
      </div>

      {query.isLoading ? (
        <Spinner />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : participants.length === 0 ? (
        <EmptyState title="No participants yet" description="Add students working on this project." />
      ) : (
        <Table columns={columns} rows={participants} />
      )}

      <Modal open={modalOpen} title={editing ? "Edit participant" : "Add participant"} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Field label="Name" htmlFor="name">
            <Input id="name" name="name" required minLength={2} defaultValue={editing?.name} />
          </Field>
          <Field label="Department" htmlFor="department">
            <Input id="department" name="department" defaultValue={editing?.department ?? ""} />
          </Field>
          <Field label="Academic year" htmlFor="academic_year">
            <Input id="academic_year" name="academic_year" defaultValue={editing?.academic_year ?? ""} />
          </Field>
          <Field label="Registration ID" htmlFor="registration_id">
            <Input id="registration_id" name="registration_id" defaultValue={editing?.registration_id ?? ""} />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createParticipant.isPending || updateParticipant.isPending}>
            {editing ? "Save changes" : "Add participant"}
          </Button>
        </form>
      </Modal>
    </div>
  );
}
