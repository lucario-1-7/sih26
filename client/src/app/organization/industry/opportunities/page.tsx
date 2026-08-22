"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { useRouter } from "next/navigation";

import { useProjectsList } from "@/hooks/useProjectQueries";
import { useCreateCollaboration } from "@/hooks/useCollaborationQueries";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Modal } from "@/components/ui/Modal";
import { PageHeader } from "@/components/ui/PageHeader";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { CollaborationType, ProjectResponse } from "@/types/api";

const TYPES: CollaborationType[] = ["funding", "mentoring", "equipment", "technical_support", "pilot_support", "other"];

/**
 * "All projects" — the backend does not expose a dedicated industry
 * opportunity-discovery feed (no GET /industry/opportunities endpoint
 * exists). This reuses the existing project-listing endpoint rather than
 * inventing one; it is intentionally NOT labeled a "matched" feed since no
 * relevance ranking is applied here (that exists per-cluster via
 * /matching/clusters/{id}, not as a project-level opportunity list).
 */
export default function OpportunitiesPage() {
  const router = useRouter();
  const query = useProjectsList({ status: "proposed" });
  const createCollaboration = useCreateCollaboration();
  const [target, setTarget] = useState<ProjectResponse | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const projects = query.data?.items ?? [];

  async function handlePropose(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!target) return;
    const form = new FormData(e.currentTarget);
    const type = String(form.get("type") ?? "") as CollaborationType;

    setFormError(null);
    try {
      const collaboration = await createCollaboration.mutateAsync({ project_id: target.id, type });
      setTarget(null);
      router.push(`/organization/industry/collaborations/${collaboration.id}`);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader
        title="All Projects"
        description="Projects open for collaboration. This is the full list, not an AI-ranked match — express interest to start a collaboration."
      />

      {query.isLoading ? (
        <Spinner label="Loading projects…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : projects.length === 0 ? (
        <EmptyState title="No open projects right now" />
      ) : (
        <div className="flex flex-col gap-3">
          {projects.map((project) => (
            <Card key={project.id} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">{project.title}</p>
                <StatusBadge status={project.status} />
              </div>
              <Button onClick={() => setTarget(project)}>Express interest</Button>
            </Card>
          ))}
        </div>
      )}

      <Modal open={target !== null} title="Express interest" onClose={() => setTarget(null)}>
        <form onSubmit={handlePropose} className="flex flex-col gap-4">
          <p className="text-sm text-slate-500">
            This starts a collaboration in the <strong>Interested</strong> state — the university reviews and accepts
            before it becomes active.
          </p>
          <label className="flex flex-col gap-1 text-sm font-medium text-slate-700" htmlFor="collab-type">
            Collaboration type
            <Select id="collab-type" name="type" required defaultValue="">
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
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createCollaboration.isPending}>
            Express interest
          </Button>
        </form>
      </Modal>
    </div>
  );
}
