"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth/AuthContext";
import { Spinner } from "@/components/ui/Spinner";
import { Topbar } from "@/components/layout/Topbar";

const ORGANIZATIONAL_DOMAINS = new Set(["government", "university", "industry", "superadmin"]);

/**
 * Shared shell for the Organizational Dashboard (Government / University /
 * Industry / Superadmin). Only University is implemented behind it in this
 * change — see app/organization/university — but the shell itself is
 * domain-agnostic so Government/Industry/Superadmin can be added later
 * without restructuring this layout.
 */
export default function OrganizationLayout({ children }: { children: ReactNode }) {
  const { user, status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "loading") return;
    if (status === "unauthenticated" || !user) {
      router.replace("/login");
      return;
    }
    if (!ORGANIZATIONAL_DOMAINS.has(user.domain)) {
      // Citizens (and any other non-organizational domain) don't belong here.
      router.replace("/citizen");
    }
  }, [status, user, router]);

  if (status === "loading" || !user || !ORGANIZATIONAL_DOMAINS.has(user.domain)) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner label="Loading dashboard…" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar />
      <div className="flex flex-1">{children}</div>
    </div>
  );
}
