"use client";

import Link from "next/link";

import { useChallengeAnalytics, useProjectAnalytics } from "@/hooks/useAnalyticsQueries";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";

export default function SuperadminDashboardPage() {
  const challengeAnalytics = useChallengeAnalytics();
  const projectAnalytics = useProjectAnalytics();

  return (
    <div>
      <PageHeader title="Superadmin Overview" description="Platform-wide administrative control plane." />

      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {challengeAnalytics.isLoading ? (
          <Spinner />
        ) : challengeAnalytics.isError ? (
          <ErrorState error={challengeAnalytics.error} onRetry={() => challengeAnalytics.refetch()} />
        ) : (
          <StatCard label="Total challenges" value={challengeAnalytics.data!.total} />
        )}
        {projectAnalytics.isLoading ? (
          <Spinner />
        ) : projectAnalytics.isError ? (
          <ErrorState error={projectAnalytics.error} onRetry={() => projectAnalytics.refetch()} />
        ) : (
          <StatCard label="Total projects" value={projectAnalytics.data!.total} />
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <NavCard title="User Management" href="/organization/superadmin/users" description="Provision and manage staff logins." />
        <NavCard title="Organizations" href="/organization/superadmin/organizations" description="University/industry organization registry." />
        <NavCard title="Analytics" href="/organization/superadmin/analytics" description="Challenges, projects, industry, ML." />
        <NavCard title="Model Info" href="/organization/superadmin/model-info" description="ML model metadata and configuration." />
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <p className="text-2xl font-semibold text-slate-900">{value}</p>
      <p className="text-sm text-slate-500">{label}</p>
    </Card>
  );
}

function NavCard({ title, href, description }: { title: string; href: string; description: string }) {
  return (
    <Link href={href}>
      <Card className="h-full transition-colors hover:border-slate-400">
        <p className="font-medium text-slate-900">{title}</p>
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      </Card>
    </Link>
  );
}
