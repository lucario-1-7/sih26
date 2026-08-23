"use client";

import { useParams } from "next/navigation";

import { useProject } from "@/hooks/useProjectQueries";
import { ImpactIndicatorsPanel } from "@/components/organization/ImpactIndicatorsPanel";
import { UniversityUptake } from "@/components/organization/UniversityUptake";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function GovernmentProjectDetailsPage() {
  const params = useParams<{ id: string }>();
  const query = useProject(params.id);

  if (query.isLoading) {
    return (
      <div className="flex justify-center p-12">
        <Spinner label="Loading project…" />
      </div>
    );
  }
  if (query.isError || !query.data) {
    return <ErrorState error={query.error} onRetry={() => query.refetch()} />;
  }

  const project = query.data;

  return (
    <div>
      <PageHeader title={project.title} actions={<StatusBadge status={project.status} />} />

      <Card className="mb-6">
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Description</dt>
            <dd className="mt-1 text-sm text-slate-700">{project.description ?? "No description provided."}</dd>
          </div>
          <UniversityUptake university={project.university} />
        </dl>
      </Card>

      <Card>
        <h2 className="mb-3 text-base font-semibold text-slate-900">Impact verification</h2>
        <ImpactIndicatorsPanel projectId={project.id} />
      </Card>
    </div>
  );
}
