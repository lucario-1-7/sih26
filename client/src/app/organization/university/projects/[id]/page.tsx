"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { getCluster } from "@/lib/api/clusters";
import { useProject } from "@/hooks/useProjectQueries";
import { ConsortiumPanel } from "@/components/university/ConsortiumPanel";
import { DeliverablesPanel } from "@/components/university/DeliverablesPanel";
import { MilestonesPanel } from "@/components/university/MilestonesPanel";
import { ParticipantsPanel } from "@/components/university/ParticipantsPanel";
import { ProjectStatusActions } from "@/components/university/ProjectStatusActions";
import { SolutionPanel } from "@/components/university/SolutionPanel";
import { ImpactIndicatorsPanel } from "@/components/organization/ImpactIndicatorsPanel";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";

type Tab = "overview" | "participants" | "consortium" | "milestones" | "deliverables" | "solution" | "impact";

const TABS: { key: Tab; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "participants", label: "Participants" },
  { key: "consortium", label: "Consortium" },
  { key: "milestones", label: "Milestones" },
  { key: "deliverables", label: "Deliverables" },
  { key: "solution", label: "Solution" },
  { key: "impact", label: "Impact" },
];

export default function ProjectDetailsPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;
  const [tab, setTab] = useState<Tab>("overview");

  const query = useProject(projectId);

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

  return <ProjectDetailsView project={project} tab={tab} setTab={setTab} />;
}

function ProjectDetailsView({
  project,
  tab,
  setTab,
}: {
  project: NonNullable<ReturnType<typeof useProject>["data"]>;
  tab: Tab;
  setTab: (tab: Tab) => void;
}) {
  const clusterQuery = useQuery({
    queryKey: ["clusters", project.cluster_id],
    queryFn: () => getCluster(project.cluster_id),
  });

  return (
    <div>
      <PageHeader
        title={project.title}
        description={`Created ${new Date(project.created_at).toLocaleDateString()} · Last updated ${new Date(
          project.updated_at,
        ).toLocaleDateString()}`}
        actions={<StatusBadge status={project.status} />}
      />

      <Card className="mb-6">
        <h2 className="mb-2 text-sm font-semibold text-slate-700">Status</h2>
        <ProjectStatusActions project={project} />
      </Card>

      <div role="tablist" aria-label="Project sections" className="mb-4 flex gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t.key}
            role="tab"
            type="button"
            aria-selected={tab === t.key}
            onClick={() => setTab(t.key)}
            className={`border-b-2 px-3 py-2 text-sm font-medium ${
              tab === t.key ? "border-slate-900 text-slate-900" : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div role="tabpanel">
        {tab === "overview" ? (
          <Card>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-xs font-medium uppercase text-slate-400">Description</dt>
                <dd className="mt-1 text-sm text-slate-700">{project.description ?? "No description provided."}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase text-slate-400">Source cluster</dt>
                <dd className="mt-1 text-sm text-slate-700">
                  {clusterQuery.data?.title ?? (clusterQuery.isLoading ? "Loading…" : project.cluster_id)}
                </dd>
              </div>
            </dl>
          </Card>
        ) : null}
        {tab === "participants" ? <ParticipantsPanel projectId={project.id} /> : null}
        {tab === "consortium" ? <ConsortiumPanel projectId={project.id} /> : null}
        {tab === "milestones" ? <MilestonesPanel projectId={project.id} /> : null}
        {tab === "deliverables" ? <DeliverablesPanel projectId={project.id} /> : null}
        {tab === "solution" ? <SolutionPanel projectId={project.id} /> : null}
        {tab === "impact" ? <ImpactIndicatorsPanel projectId={project.id} /> : null}
      </div>
    </div>
  );
}
