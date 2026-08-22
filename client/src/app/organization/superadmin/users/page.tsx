"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useCreateUser, useUpdateUser, useUsersList } from "@/hooks/useUserManagementQueries";
import { useCursorPagination, useSyncCursorPage } from "@/hooks/useCursorPagination";
import { Button } from "@/components/ui/Button";
import { DomainBadge } from "@/components/ui/DomainBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { Field, Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { PageHeader } from "@/components/ui/PageHeader";
import { RoleBadge } from "@/components/ui/RoleBadge";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { Table, type Column } from "@/components/ui/Table";
import { VALID_DOMAIN_ROLES } from "@/types/api";
import type { Domain, Role, UserResponse } from "@/types/api";

const ALL_DOMAINS: Domain[] = ["citizen", "government", "university", "industry", "superadmin"];

function DomainRoleFields({
  domain,
  role,
  onDomainChange,
  onRoleChange,
  idPrefix,
}: {
  domain: Domain;
  role: Role | "";
  onDomainChange: (d: Domain) => void;
  onRoleChange: (r: Role) => void;
  idPrefix: string;
}) {
  const validRoles = VALID_DOMAIN_ROLES[domain] ?? [];
  return (
    <div className="flex gap-3">
      <label className="flex flex-1 flex-col gap-1 text-sm font-medium text-slate-700" htmlFor={`${idPrefix}-domain`}>
        Domain
        <Select
          id={`${idPrefix}-domain`}
          value={domain}
          onChange={(e) => onDomainChange(e.target.value as Domain)}
        >
          {ALL_DOMAINS.filter((d) => d !== "citizen").map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </Select>
      </label>
      <label className="flex flex-1 flex-col gap-1 text-sm font-medium text-slate-700" htmlFor={`${idPrefix}-role`}>
        Role
        {/* Only backend-valid roles for the selected domain are offered — see
           VALID_DOMAIN_ROLES, mirroring server/app/models/enums.py. The
           backend still re-validates this independently. */}
        <Select id={`${idPrefix}-role`} value={role} onChange={(e) => onRoleChange(e.target.value as Role)} required>
          <option value="" disabled>
            Select a role…
          </option>
          {validRoles.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </Select>
      </label>
    </div>
  );
}

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [roleFilter, setRoleFilter] = useState<Role | undefined>(undefined);
  const pagination = useCursorPagination<UserResponse>();
  const query = useUsersList({ role: roleFilter, cursor: pagination.queryCursor });
  useSyncCursorPage(pagination, query.data);

  const createUser = useCreateUser();

  const [createOpen, setCreateOpen] = useState(false);
  const [createDomain, setCreateDomain] = useState<Domain>("government");
  const [createRole, setCreateRole] = useState<Role | "">("");
  const [formError, setFormError] = useState<string | null>(null);

  const [editing, setEditing] = useState<UserResponse | null>(null);
  const [editDomain, setEditDomain] = useState<Domain>("government");
  const [editRole, setEditRole] = useState<Role | "">("");
  const [editError, setEditError] = useState<string | null>(null);

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    setFormError(null);
    try {
      await createUser.mutateAsync({
        phone: String(form.get("phone") ?? "").trim(),
        name: String(form.get("name") ?? "").trim(),
        role: createRole as Role,
        domain: createDomain,
        organization_id: String(form.get("organization_id") ?? "").trim() || null,
      });
      setCreateOpen(false);
      setCreateRole("");
    } catch (err) {
      setFormError(errorMessage(err));
    }
  }

  function openEdit(u: UserResponse) {
    setEditing(u);
    setEditDomain(u.domain);
    setEditRole(u.role);
    setEditError(null);
  }

  const columns: Column<UserResponse>[] = [
    { key: "name", header: "Name", render: (u) => u.name },
    { key: "phone", header: "Phone", render: (u) => <span className="font-mono">{u.phone}</span> },
    { key: "domain", header: "Domain", render: (u) => <DomainBadge domain={u.domain} /> },
    { key: "role", header: "Role", render: (u) => <RoleBadge role={u.role} /> },
    { key: "active", header: "Active", render: (u) => (u.is_active ? "Yes" : "No") },
    {
      key: "actions",
      header: "",
      render: (u) => (
        <Button variant="ghost" onClick={() => openEdit(u)}>
          Edit
        </Button>
      ),
    },
  ];

  const showInitialLoading = query.isLoading && pagination.items.length === 0;

  return (
    <div>
      <PageHeader
        title="User Management"
        description="Provision logins for Government/University/Industry/Superadmin staff. Citizens self-provision via OTP."
        actions={
          <div className="flex items-center gap-2">
            <Select
              aria-label="Filter by role"
              value={roleFilter ?? ""}
              onChange={(e) => {
                setRoleFilter((e.target.value || undefined) as Role | undefined);
                pagination.reset();
              }}
            >
              <option value="">All roles</option>
              {(["validator", "field_assistant", "coordinator", "faculty", "industry", "superadmin", "citizen"] as Role[]).map(
                (r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ),
              )}
            </Select>
            <Button onClick={() => setCreateOpen(true)}>New user</Button>
          </div>
        }
      />

      {showInitialLoading ? (
        <Spinner label="Loading users…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : pagination.items.length === 0 ? (
        <EmptyState title="No users found" />
      ) : (
        <Table columns={columns} rows={pagination.items} />
      )}

      {pagination.hasNext ? (
        <div className="mt-4 flex justify-center">
          <Button variant="secondary" onClick={pagination.loadMore} disabled={query.isFetching}>
            {query.isFetching ? "Loading…" : "Load more"}
          </Button>
        </div>
      ) : null}

      <Modal open={createOpen} title="New user" onClose={() => setCreateOpen(false)}>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <Field label="Phone" htmlFor="u-phone">
            <Input id="u-phone" name="phone" required minLength={8} placeholder="+91XXXXXXXXXX" />
          </Field>
          <Field label="Name" htmlFor="u-name">
            <Input id="u-name" name="name" required minLength={2} />
          </Field>
          <DomainRoleFields
            domain={createDomain}
            role={createRole}
            onDomainChange={(d) => {
              setCreateDomain(d);
              setCreateRole("");
            }}
            onRoleChange={setCreateRole}
            idPrefix="create"
          />
          <Field label="Organization ID (required for University/Industry)" htmlFor="u-org">
            <Input id="u-org" name="organization_id" className="font-mono" />
          </Field>
          {formError ? (
            <p role="alert" className="text-sm text-red-600">
              {formError}
            </p>
          ) : null}
          <Button type="submit" disabled={createUser.isPending || !createRole}>
            Create user
          </Button>
        </form>
      </Modal>

      <Modal open={editing !== null} title="Edit user" onClose={() => setEditing(null)}>
        {editing ? (
          <EditUserForm
            user={editing}
            domain={editDomain}
            role={editRole}
            onDomainChange={(d) => {
              setEditDomain(d);
              setEditRole("");
            }}
            onRoleChange={setEditRole}
            error={editError}
            isSelf={currentUser?.id === editing.id}
            onClose={() => setEditing(null)}
            onSubmitError={setEditError}
          />
        ) : null}
      </Modal>
    </div>
  );
}

function EditUserForm({
  user,
  domain,
  role,
  onDomainChange,
  onRoleChange,
  error,
  isSelf,
  onClose,
  onSubmitError,
}: {
  user: UserResponse;
  domain: Domain;
  role: Role | "";
  onDomainChange: (d: Domain) => void;
  onRoleChange: (r: Role) => void;
  error: string | null;
  isSelf: boolean;
  onClose: () => void;
  onSubmitError: (msg: string | null) => void;
}) {
  const updateUser = useUpdateUser(user.id);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    onSubmitError(null);
    try {
      await updateUser.mutateAsync({
        name: String(form.get("name") ?? "").trim() || undefined,
        role: role || undefined,
        domain: domain || undefined,
        organization_id: String(form.get("organization_id") ?? "").trim() || undefined,
        is_active: form.get("is_active") === "on",
      });
      onClose();
    } catch (err) {
      onSubmitError(errorMessage(err));
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {isSelf ? (
        <p className="rounded-md bg-amber-50 p-2 text-sm text-amber-800">
          You cannot change your own role, domain, or organization — the backend rejects self-modification of these
          fields.
        </p>
      ) : null}
      <Field label="Name" htmlFor="e-name">
        <Input id="e-name" name="name" defaultValue={user.name} minLength={2} />
      </Field>
      <DomainRoleFields
        domain={domain}
        role={role}
        onDomainChange={onDomainChange}
        onRoleChange={onRoleChange}
        idPrefix="edit"
      />
      <Field label="Organization ID" htmlFor="e-org">
        <Input id="e-org" name="organization_id" defaultValue={user.organization_id ?? ""} className="font-mono" />
      </Field>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input type="checkbox" name="is_active" defaultChecked={user.is_active} className="h-4 w-4" />
        Active
      </label>
      {error ? (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      ) : null}
      <Button type="submit" disabled={updateUser.isPending}>
        Save changes
      </Button>
    </form>
  );
}
