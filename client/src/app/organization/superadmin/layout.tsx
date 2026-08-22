"use client";

import type { ReactNode } from "react";

import { DomainGuardLayout } from "@/components/organization/DomainGuardLayout";
import { isSuperadminUser } from "@/lib/rbac/config";

export default function SuperadminLayout({ children }: { children: ReactNode }) {
  return (
    <DomainGuardLayout
      isAllowed={isSuperadminUser}
      sectionLabel="Superadmin"
      deniedMessage="You don't have access to the Superadmin dashboard."
    >
      {children}
    </DomainGuardLayout>
  );
}
