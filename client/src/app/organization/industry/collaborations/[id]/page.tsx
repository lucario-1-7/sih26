"use client";

import { useParams } from "next/navigation";

import { useCollaborationsList } from "@/hooks/useCollaborationQueries";
import { useProject } from "@/hooks/useProjectQueries";
import { CollaborationStatusActions } from "@/components/organization/CollaborationStatusActions";
import { CommitmentsPanel } from "@/components/organization/CommitmentsPanel";
import { UniversityUptake } from "@/components/organization/UniversityUptake";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";

/**
 * There is no GET /collaborations/{id} endpoint — only GET /collaborations
 * (list, scoped to the caller's own org or a project) and PATCH status. This
 * page finds the record from the list rather than inventing a detail
 * endpoint; flagged as a backend gap in the final report.
 */
export default function CollaborationDetailsPage() {
  const params = useParams<{ id: string }>();
  const query = useCollaborationsList({});

  if (query.isLoading) {
    return (
      <div className="flex justify-center p-12">
        <Spinner label="Loading collaboration…" />
      </div>
    );
  }
  if (query.isError) {
    return <ErrorState error={query.error} onRetry={() => query.refetch()} />;
  }

  const collaboration = query.data?.items.find((c) => c.id === params.id);
  if (!collaboration) {
    return (
      <div role="alert" className="rounded-lg border border-slate-200 p-6 text-sm text-slate-500">
        Collaboration not found in your organization&apos;s list.
      </div>
    );
  }

  return <CollaborationDetailsView collaboration={collaboration} />;
}

function CollaborationDetailsView({
  collaboration,
}: {
  collaboration: NonNullable<ReturnType<typeof useCollaborationsList>["data"]>["items"][number];
}) {
  const projectQuery = useProject(collaboration.project_id);
  const project = projectQuery.data;

  return (
    <div>
      <PageHeader title={`Collaboration — ${collaboration.type.replace(/_/g, " ")}`} actions={<StatusBadge status={collaboration.status} />} />

      <Card className="mb-6">
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Project</dt>
            <dd className="mt-1 text-sm text-slate-700">
              {project ? project.title : projectQuery.isLoading ? "Loading…" : collaboration.project_id}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase text-slate-400">Last updated</dt>
            <dd className="mt-1 text-sm text-slate-700">{new Date(collaboration.updated_at).toLocaleString()}</dd>
          </div>
          <UniversityUptake university={project?.university ?? null} />
          {collaboration.proposal ? (
            <div className="sm:col-span-2">
              <dt className="text-xs font-medium uppercase text-slate-400">Proposal</dt>
              <dd className="mt-1 text-sm text-slate-700">{collaboration.proposal}</dd>
            </div>
          ) : null}
        </dl>

        <div className="mt-4 border-t border-slate-100 pt-4">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Lifecycle</h2>
          <CollaborationStatusActions collaboration={collaboration} />
        </div>
      </Card>

      <Card>
        <h2 className="mb-3 text-base font-semibold text-slate-900">Commitments</h2>
        <CommitmentsPanel collaborationId={collaboration.id} />
      </Card>
    </div>
  );
}
