"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useCreateTheme, useThemesList } from "@/hooks/useThemeClusterQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { canManageClustersThemes } from "@/lib/rbac/config";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import type { ThemeResponse } from "@/types/api";

export default function ThemesPage() {
  const { user } = useAuth();
  const pagination = useCursorPagination<ThemeResponse>();
  const query = useThemesList({ cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);
  const createTheme = useCreateTheme();

  const [createOpen, setCreateOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const canManage = user ? canManageClustersThemes(user.role) : false;
  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const name = String(form.get("name") ?? "").trim();
    const description = String(form.get("description") ?? "").trim() || null;

    setFormError(null);
    try {
      await createTheme.mutateAsync({ name, description });
      setCreateOpen(false);
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader
        title="Themes"
        description="Broader systemic patterns clusters belong to."
        actions={canManage ? <Button onClick={() => setCreateOpen(true)}>New theme</Button> : undefined}
      />

      {showInitialLoading ? (
        <Spinner label="Loading themes…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No themes yet" />
      ) : (
        <div className="flex flex-col gap-3">
          {pagination.items.map((theme) => (
            <Card key={theme.id}>
              <p className="font-medium text-slate-900">{theme.name}</p>
              {theme.description ? <p className="mt-1 text-sm text-slate-500">{theme.description}</p> : null}
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

      <Modal open={createOpen} title="New theme" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Name" htmlFor="t-name">
            <Input id="t-name" name="name" required minLength={3} />
          </Field>
          <Field label="Description" htmlFor="t-description">
            <Input id="t-description" name="description" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createTheme.isPending}>
            Create theme
          </Button>
        </form>
      </Modal>
    </div>
  );
}
