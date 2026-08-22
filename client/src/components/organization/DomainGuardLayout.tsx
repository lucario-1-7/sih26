"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth/AuthContext";
import { navForRole } from "@/lib/rbac/config";
import { Sidebar } from "@/components/layout/Sidebar";
import { Spinner } from "@/components/ui/Spinner";
import type { Domain, Role } from "@/types/api";

/**
 * Shared guard + sidebar shell for every domain-specific dashboard
 * (University/Government/Industry/Superadmin). This is UX routing only —
 * the backend re-enforces every one of these checks independently on each
 * request; a client that never renders this component still can't call an
 * unauthorized endpoint successfully.
 */
export function DomainGuardLayout({
  children,
  isAllowed,
  sectionLabel,
  deniedMessage,
}: {
  children: ReactNode;
  isAllowed: (domain: Domain, role: Role) => boolean;
  sectionLabel: string;
  deniedMessage: string;
}) {
  const { user, status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status !== "authenticated" || !user) return;
    if (!isAllowed(user.domain, user.role)) {
      router.replace("/organization");
    }
  }, [status, user, router, isAllowed]);

  if (status === "loading") {
    return (
      <div className="flex flex-1 items-center justify-center">
        <Spinner label="Loading…" />
      </div>
    );
  }

  if (!user || !isAllowed(user.domain, user.role)) {
    return (
      <div className="flex flex-1 items-center justify-center p-8" role="alert">
        <p className="text-sm text-slate-500">{deniedMessage}</p>
      </div>
    );
  }

  return (
    <>
      <Sidebar items={navForRole(user.role)} sectionLabel={sectionLabel} />
      <main className="flex-1 p-6">{children}</main>
    </>
  );
}
