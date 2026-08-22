"use client";

import { useChallengeAnalytics, useIndustryAnalytics, useMLAnalytics, useProjectAnalytics } from "@/hooks/useAnalyticsQueries";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";

function CountTable({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data);
  if (entries.length === 0) return <p className="text-sm text-slate-400">No data.</p>;
  return (
    <table className="w-full text-sm">
      <tbody>
        {entries.map(([key, value]) => (
          <tr key={key} className="border-b border-slate-100 last:border-0">
            <td className="py-1.5 text-slate-600">{key}</td>
            <td className="py-1.5 text-right font-mono font-medium text-slate-900">{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function AnalyticsPage() {
  const challenges = useChallengeAnalytics();
  const projects = useProjectAnalytics();
  const industry = useIndustryAnalytics();
  const ml = useMLAnalytics();

  return (
    <div>
      <PageHeader title="Analytics" description="Real aggregates from the backend — nothing here is fabricated." />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Challenges</CardTitle>
          </CardHeader>
          {challenges.isLoading ? (
            <Spinner />
          ) : challenges.isError ? (
            <ErrorState error={challenges.error} onRetry={() => challenges.refetch()} />
          ) : (
            <div>
              <p className="mb-3 text-2xl font-semibold text-slate-900">{challenges.data!.total}</p>
              <p className="mb-1 text-xs font-medium uppercase text-slate-400">By status</p>
              <CountTable data={challenges.data!.by_status} />
              <p className="mb-1 mt-3 text-xs font-medium uppercase text-slate-400">By severity</p>
              <CountTable data={challenges.data!.by_severity} />
              <p className="mb-1 mt-3 text-xs font-medium uppercase text-slate-400">By administrative area</p>
              <CountTable data={challenges.data!.by_administrative_area} />
            </div>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          {projects.isLoading ? (
            <Spinner />
          ) : projects.isError ? (
            <ErrorState error={projects.error} onRetry={() => projects.refetch()} />
          ) : (
            <div>
              <p className="mb-3 text-2xl font-semibold text-slate-900">{projects.data!.total}</p>
              <p className="mb-1 text-xs font-medium uppercase text-slate-400">By status</p>
              <CountTable data={projects.data!.by_status} />
              <p className="mb-1 mt-3 text-xs font-medium uppercase text-slate-400">By organization</p>
              <CountTable data={projects.data!.by_organization} />
            </div>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Industry</CardTitle>
          </CardHeader>
          {industry.isLoading ? (
            <Spinner />
          ) : industry.isError ? (
            <ErrorState error={industry.error} onRetry={() => industry.refetch()} />
          ) : (
            <div>
              <div className="mb-3 grid grid-cols-2 gap-2">
                <div>
                  <p className="text-2xl font-semibold text-slate-900">{industry.data!.organization_count}</p>
                  <p className="text-xs text-slate-500">Organizations</p>
                </div>
                <div>
                  <p className="text-2xl font-semibold text-slate-900">{industry.data!.collaboration_count}</p>
                  <p className="text-xs text-slate-500">Collaborations</p>
                </div>
              </div>
              <p className="mb-1 text-xs font-medium uppercase text-slate-400">Collaborations by status</p>
              <CountTable data={industry.data!.collaborations_by_status} />
              <p className="mb-1 mt-3 text-xs font-medium uppercase text-slate-400">Commitments by status</p>
              <CountTable data={industry.data!.commitments_by_status} />
              <p className="mb-1 mt-3 text-xs font-medium uppercase text-slate-400">Commitments by type</p>
              <CountTable data={industry.data!.commitments_by_type} />
            </div>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ML</CardTitle>
          </CardHeader>
          {ml.isLoading ? (
            <Spinner />
          ) : ml.isError ? (
            <ErrorState error={ml.error} onRetry={() => ml.refetch()} />
          ) : (
            <div>
              <CountTable
                data={{
                  "Challenges embedded": ml.data!.challenges_with_embedding,
                  "Clusters embedded": ml.data!.clusters_with_embedding,
                  "Solutions embedded": ml.data!.solutions_with_embedding,
                  "Duplicate candidates generated": ml.data!.duplicate_candidates_generated,
                  "Duplicate decisions total": ml.data!.duplicate_decisions_total,
                }}
              />
              <p className="mb-1 mt-3 text-xs font-medium uppercase text-slate-400">Duplicate decisions by type</p>
              <CountTable data={ml.data!.duplicate_decisions_by_type} />
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
