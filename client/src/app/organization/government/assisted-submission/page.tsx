"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { useRouter } from "next/navigation";

import { useCreateAssistedChallenge } from "@/hooks/useChallengeQueries";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { errorMessage } from "@/components/ui/ErrorState";
import { Field, Input, Textarea } from "@/components/ui/Input";
import { PageHeader } from "@/components/ui/PageHeader";

/**
 * "Submit on behalf of citizen" — the Field Assistant never becomes the
 * citizen (submitted_by_id stays the Field Assistant's own account); the
 * backend records on_behalf_of_name/on_behalf_of_phone to preserve that the
 * report was assisted. No citizen account or password is created here.
 */
export default function AssistedSubmissionPage() {
  const router = useRouter();
  const createAssisted = useCreateAssistedChallenge();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    setError(null);
    setSuccess(false);
    try {
      await createAssisted.mutateAsync({
        title: String(form.get("title") ?? "").trim(),
        description: String(form.get("description") ?? "").trim(),
        administrative_area_id: String(form.get("administrative_area_id") ?? "").trim(),
        pin_code: String(form.get("pin_code") ?? "").trim() || null,
        on_behalf_of_name: String(form.get("on_behalf_of_name") ?? "").trim(),
        on_behalf_of_phone: String(form.get("on_behalf_of_phone") ?? "").trim(),
      });
      setSuccess(true);
      (e.target as HTMLFormElement).reset();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader title="Submit for Citizen" description="Capture a challenge on behalf of a citizen who has no account of their own." />

      <Card className="max-w-2xl">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <fieldset className="rounded-md border border-slate-200 p-4">
            <legend className="px-1 text-sm font-semibold text-slate-700">On behalf of (citizen)</legend>
            <p className="mb-3 text-xs text-slate-500">
              The citizen never gets a login — this only records that the report was assisted.
            </p>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Field label="Citizen's name" htmlFor="on_behalf_of_name">
                <Input id="on_behalf_of_name" name="on_behalf_of_name" required minLength={2} />
              </Field>
              <Field label="Citizen's phone" htmlFor="on_behalf_of_phone">
                <Input id="on_behalf_of_phone" name="on_behalf_of_phone" required minLength={8} placeholder="+91XXXXXXXXXX" />
              </Field>
            </div>
          </fieldset>

          <Field label="Title" htmlFor="title">
            <Input id="title" name="title" required minLength={5} maxLength={200} />
          </Field>
          <Field label="Description" htmlFor="description">
            <Textarea id="description" name="description" required minLength={20} rows={4} />
          </Field>
          <Field label="Administrative area ID" htmlFor="administrative_area_id">
            <Input id="administrative_area_id" name="administrative_area_id" required placeholder="UUID" className="font-mono" />
            <p className="mt-1 text-xs text-slate-500">
              No area picker is available yet — the backend doesn&apos;t expose a list endpoint for administrative
              areas. Ask your supervisor for the UUID.
            </p>
          </Field>
          <Field label="PIN code (optional)" htmlFor="pin_code">
            <Input id="pin_code" name="pin_code" maxLength={6} minLength={6} />
          </Field>

          {error ? (
            <p role="alert" className="text-sm text-red-600">
              {error}
            </p>
          ) : null}
          {success ? (
            <p role="status" className="text-sm text-green-700">
              Submitted successfully.
            </p>
          ) : null}

          <div className="flex gap-2">
            <Button type="submit" disabled={createAssisted.isPending}>
              {createAssisted.isPending ? "Submitting…" : "Submit on behalf of citizen"}
            </Button>
            <Button type="button" variant="secondary" onClick={() => router.push("/organization/government")}>
              Back to dashboard
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
