"use client";

import { useAuth } from "@/hooks/useAuth";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { DomainBadge } from "@/components/ui/DomainBadge";
import { RoleBadge } from "@/components/ui/RoleBadge";

export function ProfileView() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div>
      <PageHeader title="Profile" />
      <Card className="max-w-md">
        <dl className="flex flex-col gap-3 text-sm">
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Name</dt>
            <dd className="mt-0.5 text-slate-800">{user.name}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Phone</dt>
            <dd className="mt-0.5 font-mono text-slate-800">{user.phone}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Domain</dt>
            <dd className="mt-0.5">
              <DomainBadge domain={user.domain} />
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Role</dt>
            <dd className="mt-0.5">
              <RoleBadge role={user.role} />
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Organization ID</dt>
            <dd className="mt-0.5 font-mono text-slate-800">{user.organization_id ?? "—"}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
