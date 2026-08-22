"use client";

import { useState } from "react";

import { useUpdateProject } from "@/hooks/useProjectQueries";
import { Button } from "@/components/ui/Button";
import { errorMessage } from "@/components/ui/ErrorState";
import { PROJECT_STATUS_TRANSITIONS } from "@/types/api";
import type { ProjectResponse, ProjectStatus } from "@/types/api";

const ACTION_LABEL: Record<ProjectStatus, string> = {
  proposed: "Mark proposed",
  accepted: "Accept",
  active: "Activate",
  on_hold: "Put on hold",
  completed: "Mark completed",
  cancelled: "Cancel",
};

/** Only ever offers backend-valid transitions (see
 * app/models/enums.py::PROJECT_STATUS_TRANSITIONS) — never a free-form
 * status dropdown. If a transition is rejected server-side, the error is
 * shown and the project is refetched to the true server state. */
export function ProjectStatusActions({ project }: { project: ProjectResponse }) {
  const updateProject = useUpdateProject(project.id);
  const [error, setError] = useState<string | null>(null);
  const nextStates = PROJECT_STATUS_TRANSITIONS[project.status];

  async function transition(status: ProjectStatus) {
    setError(null);
    try {
      await updateProject.mutateAsync({ status });
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  if (nextStates.length === 0) {
    return <p className="text-sm text-slate-500">This project is in a final state.</p>;
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {nextStates.map((status) => (
          <Button
            key={status}
            variant={status === "cancelled" ? "danger" : "secondary"}
            onClick={() => void transition(status)}
            disabled={updateProject.isPending}
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
