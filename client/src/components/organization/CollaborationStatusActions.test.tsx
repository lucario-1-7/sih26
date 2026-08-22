import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CollaborationStatusActions } from "@/components/organization/CollaborationStatusActions";
import type { CollaborationResponse } from "@/types/api";

function baseCollaboration(overrides: Partial<CollaborationResponse> = {}): CollaborationResponse {
  return {
    id: "col1",
    organization_id: "org1",
    project_id: "p1",
    type: "funding",
    status: "interested",
    proposal: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("CollaborationStatusActions — only backend-valid transitions are offered", () => {
  it("interested -> only Submit proposal / Reject", () => {
    renderWithClient(<CollaborationStatusActions collaboration={baseCollaboration({ status: "interested" })} />);
    expect(screen.getByText("Submit proposal")).toBeInTheDocument();
    expect(screen.getByText("Reject")).toBeInTheDocument();
    expect(screen.queryByText("Accept")).not.toBeInTheDocument();
    expect(screen.queryByText("Activate")).not.toBeInTheDocument();
  });

  it("active -> only Mark completed (no skipping to a state not reachable)", () => {
    renderWithClient(<CollaborationStatusActions collaboration={baseCollaboration({ status: "active" })} />);
    expect(screen.getByText("Mark completed")).toBeInTheDocument();
    expect(screen.queryByText("Reject")).not.toBeInTheDocument();
  });

  it("completed/rejected are terminal — no actions offered", () => {
    renderWithClient(<CollaborationStatusActions collaboration={baseCollaboration({ status: "completed" })} />);
    expect(screen.getByText("This collaboration is in a final state.")).toBeInTheDocument();
  });
});
