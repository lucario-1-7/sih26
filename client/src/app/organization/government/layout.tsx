"use client";

import type { ReactNode } from "react";

import { DomainGuardLayout } from "@/components/organization/DomainGuardLayout";
import { isGovernmentUser } from "@/lib/rbac/config";

export default function GovernmentLayout({ children }: { children: ReactNode }) {
  return (
    <DomainGuardLayout
      isAllowed={isGovernmentUser}
      sectionLabel="Government"
      deniedMessage="You don't have access to the Government dashboard."
    >
      {children}
    </DomainGuardLayout>
  );
}
