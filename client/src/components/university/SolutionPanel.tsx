"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";

import { useAuth } from "@/hooks/useAuth";
import { useCreateSolution, useSolutionsList, useUpdateSolution } from "@/hooks/useSolutionQueries";
import { canPublishSolution } from "@/lib/rbac/config";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input, Textarea } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";

export function SolutionPanel({ projectId }: { projectId: string }) {
  const { user } = useAuth();
  const query = useSolutionsList({ project_id: projectId });
  const createSolution = useCreateSolution();
  const [formError, setFormError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const solutions = query.data?.items ?? [];

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const title = String(form.get("title") ?? "").trim();
    const outcome = String(form.get("outcome") ?? "").trim() || null;

    setFormError(null);
    try {
      await createSolution.mutateAsync({ project_id: projectId, title, outcome });
      setCreating(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  if (query.isLoading) return <Spinner />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  if (solutions.length === 0 && !creating) {
    return (
      <div>
        <EmptyState
          title="No solution registered yet"
          description="Once this project produces an outcome, register it here as a Solution."
        />
        {user && canPublishSolution(user.role) ? (
          <div className="mt-3 flex justify-center">
            <Button onClick={() => setCreating(true)}>Register solution</Button>
          </div>
        ) : null}
      </div>
    );
  }

  if (creating) {
    return (
      <form onSubmit={handleCreate} className="flex max-w-lg flex-col gap-4">
        <Field label="Title" htmlFor="s-title">
          <Input id="s-title" name="title" required minLength={3} />
        </Field>
        <Field label="Outcome" htmlFor="s-outcome">
          <Textarea id="s-outcome" name="outcome" rows={4} />
        </Field>
        {formError ? (
          <p role="alert" className="text-sm text-red-600">
            {formError}
          </p>
        ) : null}
        <div className="flex gap-2">
          <Button type="submit" disabled={createSolution.isPending}>
            Register solution
          </Button>
          <Button type="button" variant="secondary" onClick={() => setCreating(false)}>
            Cancel
          </Button>
        </div>
      </form>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {solutions.map((solution) => (
        <Card key={solution.id}>
          <div className="flex items-center justify-between">
            <Link href={`/organization/university/solutions/${solution.id}`} className="font-medium text-slate-900 hover:underline">
              {solution.title}
            </Link>
            <StatusBadge status={solution.status} />
          </div>
          {solution.outcome ? <p className="mt-2 text-sm text-slate-600">{solution.outcome}</p> : null}
        </Card>
      ))}
    </div>
  );
}
