"use client";

import Link from "next/link";

import { useAuth } from "@/hooks/useAuth";
import { useProjectsList } from "@/hooks/useProjectQueries";
import { useOpportunities } from "@/hooks/useOpportunities";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ProjectResponse, ProjectStatus } from "@/types/api";

function countByStatus(projects: ProjectResponse[], status: ProjectStatus): number {
  return projects.filter((p) => p.status === status).length;
}

export default function UniversityDashboardPage() {
  const { user } = useAuth();
  const projectsQuery = useProjectsList({});
  const opportunitiesQuery = useOpportunities();

  const isCoordinator = user?.role === "coordinator";
  const projects = projectsQuery.data?.items ?? [];
  const opportunities = opportunitiesQuery.data?.items ?? [];

  return (
    <div>
      <PageHeader
        title={isCoordinator ? "Coordinator Dashboard" : "Faculty Dashboard"}
        description="Real-time snapshot of your institution's projects and opportunities."
      />

      {projectsQuery.isLoading ? (
        <Spinner label="Loading project summary…" />
      ) : projectsQuery.isError ? (
        <ErrorState error={projectsQuery.error} onRetry={() => projectsQuery.refetch()} />
      ) : (
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Proposed" value={countByStatus(projects, "proposed")} />
          <StatCard label="Active" value={countByStatus(projects, "active")} />
          <StatCard label="On hold" value={countByStatus(projects, "on_hold")} />
          <StatCard label="Completed" value={countByStatus(projects, "completed")} />
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent projects</CardTitle>
            <Link href="/organization/university/projects" className="text-sm font-medium text-slate-600 hover:underline">
              View all
            </Link>
          </CardHeader>
          {projectsQuery.isLoading ? (
            <Spinner />
          ) : projectsQuery.isError ? (
            <ErrorState error={projectsQuery.error} onRetry={() => projectsQuery.refetch()} />
          ) : projects.length === 0 ? (
            <EmptyState title="No projects yet" description="Projects your institution creates or is assigned to will appear here." />
          ) : (
            <ul className="flex flex-col gap-3">
              {projects.slice(0, 5).map((project) => (
                <li key={project.id} className="flex items-center justify-between text-sm">
                  <Link
                    href={`/organization/university/projects/${project.id}`}
                    className="font-medium text-slate-900 hover:underline"
                  >
                    {project.title}
                  </Link>
                  <StatusBadge status={project.status} />
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Relevant opportunities</CardTitle>
            <Link href="/organization/university/opportunities" className="text-sm font-medium text-slate-600 hover:underline">
              View all
            </Link>
          </CardHeader>
          {opportunitiesQuery.isLoading ? (
            <Spinner />
          ) : opportunitiesQuery.isError ? (
            <ErrorState error={opportunitiesQuery.error} onRetry={() => opportunitiesQuery.refetch()} />
          ) : opportunities.length === 0 ? (
            <EmptyState title="No open opportunities" description="Active systemic clusters not yet attached to a project will appear here." />
          ) : (
            <ul className="flex flex-col gap-3">
              {opportunities.slice(0, 5).map((cluster) => (
                <li key={cluster.id} className="text-sm font-medium text-slate-900">
                  {cluster.title}
                </li>
              ))}
            </ul>
          )}
        </Card>
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
