"use client";

import { useAuth } from "@/lib/auth/AuthContext";
import { Button } from "@/components/ui/Button";

const ROLE_LABEL: Record<string, string> = {
  coordinator: "Coordinator",
  faculty: "Faculty",
};

export function Topbar({ organizationName }: { organizationName?: string }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
      <div>
        <p className="text-sm font-semibold text-slate-900">Sahyog — Organizational Dashboard</p>
        {organizationName ? <p className="text-xs text-slate-500">{organizationName}</p> : null}
      </div>
      <div className="flex items-center gap-4">
        {user ? (
          <div className="text-right text-sm">
            <p className="font-medium text-slate-900">{user.name}</p>
            <p className="text-xs text-slate-500">{ROLE_LABEL[user.role] ?? user.role}</p>
          </div>
        ) : null}
        <Button variant="secondary" onClick={() => void logout()}>
          Sign out
        </Button>
      </div>
    </header>
  );
}
