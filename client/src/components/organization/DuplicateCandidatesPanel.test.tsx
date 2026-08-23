import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api/duplicate", () => ({
  listDuplicateCandidates: vi.fn(),
  createDuplicateDecision: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({ useAuth: vi.fn() }));

import { listDuplicateCandidates } from "@/lib/api/duplicate";
import { useAuth } from "@/hooks/useAuth";
import { DuplicateCandidatesPanel } from "@/components/organization/DuplicateCandidatesPanel";
import type { ChallengeResponse, DuplicateCandidateResponse } from "@/types/api";

function baseChallenge(overrides: Partial<ChallengeResponse> = {}): ChallengeResponse {
  return {
    id: "c1",
    title: "Broken streetlight",
    description: "A streetlight has been broken for two weeks.",
    status: "open",
    severity: null,
    submitted_by_id: "u1",
    administrative_area_id: "a1",
    pin_code: null,
    cluster_id: null,
    duplicate_of_id: null,
    on_behalf_of_name: null,
    on_behalf_of_phone: null,
    content_domain: null,
    content_domain_confidence: null,
    content_domain_needs_review: null,
    content_domain_source: null,
    content_field_intensity: null,
    content_field_label: null,
    content_field_needs_review: null,
    content_field_source: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

const CANDIDATE: DuplicateCandidateResponse = {
  id: "d1",
  challenge_id: "c1",
  candidate_challenge_id: "c2",
  similarity_score: 0.91,
  model_name: "paraphrase-multilingual-MiniLM-L12-v2",
  model_version: "1",
  created_at: "2026-01-01T00:00:00Z",
};

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("DuplicateCandidatesPanel — RBAC visibility", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(listDuplicateCandidates).mockResolvedValue([CANDIDATE]);
  });

  it("labels candidates as evidence/recommendation, never an automatic determination", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: { role: "validator" } } as never);
    renderWithClient(<DuplicateCandidatesPanel challenge={baseChallenge()} />);
    await waitFor(() => expect(screen.getByText(/Recommendation \/ evidence/i)).toBeInTheDocument());
    expect(screen.queryByText(/automatically identified/i)).not.toBeInTheDocument();
  });

  it("Validator sees decision actions", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: { role: "validator" } } as never);
    renderWithClient(<DuplicateCandidatesPanel challenge={baseChallenge()} />);
    await waitFor(() => expect(screen.getByText("Mark duplicate")).toBeInTheDocument());
    expect(screen.getByText("Not a duplicate")).toBeInTheDocument();
  });

  it("Field Assistant does NOT see decision actions (frontend UX only — backend also enforces 403)", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: { role: "field_assistant" } } as never);
    renderWithClient(<DuplicateCandidatesPanel challenge={baseChallenge()} />);
    await waitFor(() => expect(screen.getByText(CANDIDATE.model_name, { exact: false })).toBeInTheDocument());
    expect(screen.queryByText("Mark duplicate")).not.toBeInTheDocument();
    expect(screen.queryByText("Not a duplicate")).not.toBeInTheDocument();
  });

  it("shows the current effective decision with reversibility note when challenge is marked duplicate", async () => {
    vi.mocked(useAuth).mockReturnValue({ user: { role: "validator" } } as never);
    renderWithClient(
      <DuplicateCandidatesPanel challenge={baseChallenge({ status: "duplicate", duplicate_of_id: "c2" })} />,
    );
    await waitFor(() => expect(screen.getByText(/Current effective decision/i)).toBeInTheDocument());
    expect(screen.getByText(/append-only and reversible/i)).toBeInTheDocument();
  });
});
