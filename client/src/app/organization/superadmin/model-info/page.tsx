"use client";

import { useModelInfo } from "@/hooks/useAnalyticsQueries";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";

export default function ModelInfoPage() {
  const query = useModelInfo();

  return (
    <div>
      <PageHeader title="Model Information" description="ML configuration and metadata — no credentials or secrets." />

      {query.isLoading ? (
        <Spinner label="Loading model info…" />
      ) : query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : (
        <Card className="max-w-lg">
          <dl className="flex flex-col gap-3 text-sm">
            <Row label="Model name" value={query.data!.model_name} mono />
            <Row label="Embedding dimension" value={String(query.data!.embedding_dimension)} mono />
            <Row label="Duplicate similarity threshold" value={String(query.data!.duplicate_similarity_threshold)} mono />
            <Row label="Duplicate candidate limit" value={String(query.data!.duplicate_candidate_limit)} mono />
            <Row label="ML service URL" value={query.data!.ml_service_url} mono />
          </dl>
        </Card>
      )}
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase text-slate-400">{label}</dt>
      <dd className={`mt-0.5 text-slate-800 ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  );
}
