"use client";

import type { ReactNode } from "react";

import { DomainGuardLayout } from "@/components/organization/DomainGuardLayout";
import { isIndustryUser } from "@/lib/rbac/config";

export default function IndustryLayout({ children }: { children: ReactNode }) {
  return (
    <DomainGuardLayout
      isAllowed={isIndustryUser}
      sectionLabel="Industry"
      deniedMessage="You don't have access to the Industry dashboard."
    >
      {children}
    </DomainGuardLayout>
  );
}
