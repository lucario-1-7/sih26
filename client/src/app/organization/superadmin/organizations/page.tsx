"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useCreateOrganization, useOrganizationsList } from "@/hooks/useOrganizationQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { PageHeader } from "@/components/ui/PageHeader";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import type { OrganizationResponse, OrganizationType } from "@/types/api";

export default function OrganizationsPage() {
  const pagination = useCursorPagination<OrganizationResponse>();
  const query = useOrganizationsList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);
  const createOrganization = useCreateOrganization();

  const [createOpen, setCreateOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const name = String(form.get("name") ?? "").trim();
    const type = String(form.get("type") ?? "") as OrganizationType;
    const description = String(form.get("description") ?? "").trim() || null;

    setFormError(null);
    try {
      await createOrganization.mutateAsync({ name, type, description });
      setCreateOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader
        title="Organizations"
        description="University/industry organization registry. No edit endpoint exists yet — create only."
        actions={<Button onClick={() => setCreateOpen(true)}>New organization</Button>}
      />

      {showInitialLoading ? (
        <Spinner label="Loading organizations…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No organizations yet" />
      ) : (
        <div className="flex flex-col gap-3">
          {pagination.items.map((org) => (
            <Card key={org.id} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">{org.name}</p>
                {org.description ? <p className="mt-1 text-sm text-slate-500">{org.description}</p> : null}
              </div>
              <Badge tone="neutral">{org.type}</Badge>
            </Card>
          ))}
        </div>
      )}

      {pagination.hasNext ? (
        <div className="mt-4 flex justify-center">
          <Button variant="secondary" onClick={pagination.loadMore} disabled={query.isFetching}>
            {query.isFetching ? "Loading…" : "Load more"}
          </Button>
        </div>
      ) : null}

      <Modal open={createOpen} title="New organization" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Name" htmlFor="o-name">
            <Input id="o-name" name="name" required minLength={2} />
          </Field>
          <label className="flex flex-col gap-1 text-sm font-medium text-slate-700" htmlFor="o-type">
            Type
            <Select id="o-type" name="type" required defaultValue="">
              <option value="" disabled>
                Select a type…
              </option>
              <option value="university">university</option>
              <option value="industry">industry</option>
            </Select>
          </label>
          <Field label="Description" htmlFor="o-description">
            <Input id="o-description" name="description" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createOrganization.isPending}>
            Create organization
          </Button>
        </form>
      </Modal>
    </div>
  );
}
