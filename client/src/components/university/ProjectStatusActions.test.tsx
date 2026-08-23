import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectStatusActions } from "@/components/university/ProjectStatusActions";
import type { ProjectResponse } from "@/types/api";

vi.mock("@/lib/api/projects", () => ({
  updateProject: vi.fn(),
  getProject: vi.fn(),
  listProjects: vi.fn(),
  createProject: vi.fn(),
}));

import { updateProject } from "@/lib/api/projects";

function baseProject(overrides: Partial<ProjectResponse> = {}): ProjectResponse {
  return {
    id: "p1",
    cluster_id: "c1",
    title: "Water pipe replacement",
    description: null,
    status: "proposed",
    owner_id: "u1",
    organization_id: "org1",
    university: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("ProjectStatusActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows only valid transitions for a proposed project", () => {
    renderWithClient(<ProjectStatusActions project={baseProject({ status: "proposed" })} />);
    expect(screen.getByText("Accept")).toBeInTheDocument();
    expect(screen.getByText("Cancel")).toBeInTheDocument();
    expect(screen.queryByText("Activate")).not.toBeInTheDocument();
    expect(screen.queryByText("Mark completed")).not.toBeInTheDocument();
  });

  it("shows no actions for a completed (terminal) project", () => {
    renderWithClient(<ProjectStatusActions project={baseProject({ status: "completed" })} />);
    expect(screen.getByText("This project is in a final state.")).toBeInTheDocument();
  });

  it("calls updateProject with the chosen status when an action is clicked", async () => {
    vi.mocked(updateProject).mockResolvedValue(baseProject({ status: "accepted" }));
    renderWithClient(<ProjectStatusActions project={baseProject({ status: "proposed" })} />);

    screen.getByText("Accept").click();

    await waitFor(() => expect(updateProject).toHaveBeenCalledWith("p1", { status: "accepted" }));
  });

  it("displays the backend error message and does not crash when a transition is rejected", async () => {
    class ApiErrorStub extends Error {
      status = 409;
      code = "INVALID_STATUS_TRANSITION";
    }
    vi.mocked(updateProject).mockRejectedValue(new ApiErrorStub("Cannot move a project from proposed to active"));

    renderWithClient(<ProjectStatusActions project={baseProject({ status: "proposed" })} />);
    screen.getByText("Accept").click();

    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
  });
});
