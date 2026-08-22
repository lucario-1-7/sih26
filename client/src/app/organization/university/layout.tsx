"use client";

import type { ReactNode } from "react";

import { DomainGuardLayout } from "@/components/organization/DomainGuardLayout";
import { isUniversityUser } from "@/lib/rbac/config";

export default function UniversityLayout({ children }: { children: ReactNode }) {
  return (
    <DomainGuardLayout
      isAllowed={isUniversityUser}
      sectionLabel="University"
      deniedMessage="You don't have access to the University dashboard."
    >
      {children}
    </DomainGuardLayout>
  );
}
