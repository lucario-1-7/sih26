"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import {
  useCreateImpactIndicator,
  useImpactIndicatorsList,
  useSubmitEndline,
  useVerifyImpactIndicator,
} from "@/hooks/useImpactIndicatorQueries";
import { canManageProjectContent, canVerifyImpact } from "@/lib/rbac/config";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Spinner } from "@/components/ui/Spinner";
import type { ImpactIndicatorResponse } from "@/types/api";

/** Distinguishes Baseline / Claimed Endline / Independently Verified — a
 * project reaching COMPLETED never implies verified impact; verification is
 * a separate, explicit action restricted to Validator/Superadmin. */
function impactState(indicator: ImpactIndicatorResponse): { label: string; tone: "neutral" | "info" | "success" } {
  if (indicator.verified_at) return { label: "Verified", tone: "success" };
  if (indicator.actual_value !== null) return { label: "Pending verification", tone: "info" };
  return { label: "Not measured", tone: "neutral" };
}

export function ImpactIndicatorsPanel({ projectId }: { projectId: string }) {
  const { user } = useAuth();
  const query = useImpactIndicatorsList(projectId);
  const createIndicator = useCreateImpactIndicator(projectId);
  const submitEndline = useSubmitEndline(projectId);
  const verifyIndicator = useVerifyImpactIndicator(projectId);

  const [createOpen, setCreateOpen] = useState(false);
  const [endlineTarget, setEndlineTarget] = useState<ImpactIndicatorResponse | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const indicators = query.data?.items ?? [];
  const canManage = user ? canManageProjectContent(user.role) : false;
  const canVerify = user ? canVerifyImpact(user.role) : false;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const name = String(form.get("name") ?? "").trim();
    const unit = String(form.get("unit") ?? "").trim();
    const baseline_value = form.get("baseline_value") ? Number(form.get("baseline_value")) : null;
    const target_value = form.get("target_value") ? Number(form.get("target_value")) : null;
    const baseline_date = String(form.get("baseline_date") ?? "").trim() || null;

    setFormError(null);
    try {
      await createIndicator.mutateAsync({ name, unit, baseline_value, target_value, baseline_date });
      setCreateOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  async function handleSubmitEndline(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!endlineTarget) return;
    const form = new FormData(e.currentTarget);
    const actual_value = Number(form.get("actual_value"));
    const endline_date = String(form.get("endline_date") ?? "");
    const endline_evidence = String(form.get("endline_evidence") ?? "").trim() || null;

    setFormError(null);
    try {
      await submitEndline.mutateAsync({ indicatorId: endlineTarget.id, data: { actual_value, endline_date, endline_evidence } });
      setEndlineTarget(null);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  async function handleVerify(indicator: ImpactIndicatorResponse, approve: boolean) {
    setActionError(null);
    try {
      await verifyIndicator.mutateAsync({ indicatorId: indicator.id, approve });
    } catch (err) {
      setActionError(errorMessage(err));
    }
  }

  if (query.isLoading) return <Spinner />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  return (
    <div>
      {canManage ? (
        <div className="mb-3 flex justify-end">
          <Button onClick={() => setCreateOpen(true)}>Declare indicator</Button>
        </div>
      ) : null}

      {actionError ? (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {actionError}
        </p>
      ) : null}

      {indicators.length === 0 ? (
        <EmptyState title="No impact indicators declared" description="Indicators are declared with a baseline before implementation." />
      ) : (
        <div className="flex flex-col gap-3">
          {indicators.map((indicator) => {
            const state = impactState(indicator);
            return (
              <div key={indicator.id} className="rounded-lg border border-slate-200 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <p className="font-medium text-slate-900">{indicator.name}</p>
                  <Badge tone={state.tone}>{state.label}</Badge>
                </div>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm sm:grid-cols-4">
                  <div>
                    <dt className="text-xs text-slate-400">Baseline</dt>
                    <dd className="font-mono text-slate-700">
                      {indicator.baseline_value ?? "—"} {indicator.unit}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-400">Target</dt>
                    <dd className="font-mono text-slate-700">
                      {indicator.target_value ?? "—"} {indicator.unit}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-400">Claimed endline</dt>
                    <dd className="font-mono text-slate-700">
                      {indicator.actual_value ?? "—"} {indicator.unit}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-400">Verified</dt>
                    <dd className="text-slate-700">{indicator.verified_at ? "Yes" : "No"}</dd>
                  </div>
                </dl>

                <div className="mt-3 flex gap-2">
                  {canManage && indicator.actual_value === null ? (
                    <Button variant="secondary" onClick={() => setEndlineTarget(indicator)}>
                      Submit endline
                    </Button>
                  ) : null}
                  {canVerify && indicator.actual_value !== null && !indicator.verified_at ? (
                    <>
                      <Button variant="secondary" onClick={() => void handleVerify(indicator, true)}>
                        Verify
                      </Button>
                      <Button variant="ghost" onClick={() => void handleVerify(indicator, false)}>
                        Reject verification
                      </Button>
                    </>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <Modal open={createOpen} title="Declare impact indicator" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Name" htmlFor="i-name">
            <Input id="i-name" name="name" required minLength={3} placeholder="e.g. pump_downtime_days" />
          </Field>
          <Field label="Unit" htmlFor="i-unit">
            <Input id="i-unit" name="unit" required placeholder="e.g. days" />
          </Field>
          <Field label="Baseline value" htmlFor="i-baseline_value">
            <Input id="i-baseline_value" name="baseline_value" type="number" step="any" />
          </Field>
          <Field label="Baseline date" htmlFor="i-baseline_date">
            <Input id="i-baseline_date" name="baseline_date" type="date" />
          </Field>
          <Field label="Target value" htmlFor="i-target_value">
            <Input id="i-target_value" name="target_value" type="number" step="any" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createIndicator.isPending}>
            Declare indicator
          </Button>
        </form>
      </Modal>

      <Modal open={endlineTarget !== null} title="Submit claimed endline" onClose={() => setEndlineTarget(null)}>
        <form onSubmit={handleSubmitEndline} className="flex flex-col gap-4">
          <p className="text-sm text-slate-500">
            This is a claimed value, not yet verified. A Validator or Superadmin independently verifies it separately.
          </p>
          <Field label="Actual value" htmlFor="e-actual_value">
            <Input id="e-actual_value" name="actual_value" type="number" step="any" required />
          </Field>
          <Field label="Endline date" htmlFor="e-endline_date">
            <Input id="e-endline_date" name="endline_date" type="date" required />
          </Field>
          <Field label="Evidence" htmlFor="e-endline_evidence">
            <Input id="e-endline_evidence" name="endline_evidence" placeholder="Link or description" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={submitEndline.isPending}>
            Submit claimed endline
          </Button>
        </form>
      </Modal>
    </div>
  );
}
