"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth/AuthContext";
import { Spinner } from "@/components/ui/Spinner";
import type { Domain } from "@/types/api";

const DOMAIN_ROUTE: Partial<Record<Domain, string>> = {
  university: "/organization/university",
  government: "/organization/government",
  industry: "/organization/industry",
  superadmin: "/organization/superadmin",
};

/** Routes an authenticated organizational user to their domain's dashboard,
 * driven entirely by the actual /users/me response — never by phone number
 * or a hardcoded mapping. */
export default function OrganizationIndexPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) return;
    const target = DOMAIN_ROUTE[user.domain];
    if (target) router.replace(target);
  }, [user, router]);

  return (
    <div className="flex flex-1 items-center justify-center">
      <Spinner label="Redirecting…" />
    </div>
  );
}
