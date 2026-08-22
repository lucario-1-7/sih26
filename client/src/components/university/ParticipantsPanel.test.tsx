import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ParticipantsPanel } from "@/components/university/ParticipantsPanel";
import type { PaginatedResponse, ProjectParticipantResponse } from "@/types/api";

vi.mock("@/lib/api/participants", () => ({
  listParticipants: vi.fn(),
  createParticipant: vi.fn(),
  updateParticipant: vi.fn(),
}));

import { createParticipant, listParticipants } from "@/lib/api/participants";

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

const EMPTY_PAGE: PaginatedResponse<ProjectParticipantResponse> = { items: [], next_cursor: null, total: 0 };

describe("ParticipantsPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows an empty state when there are no participants", async () => {
    vi.mocked(listParticipants).mockResolvedValue(EMPTY_PAGE);
    renderWithClient(<ParticipantsPanel projectId="p1" />);
    await waitFor(() => expect(screen.getByText("No participants yet")).toBeInTheDocument());
  });

  it("lists existing participants", async () => {
    vi.mocked(listParticipants).mockResolvedValue({
      items: [
        {
          id: "part1",
          project_id: "p1",
          name: "Asha Verma",
          department: "Civil",
          academic_year: "3",
          registration_id: null,
          participation_role: "member",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      next_cursor: null,
      total: 1,
    });
    renderWithClient(<ParticipantsPanel projectId="p1" />);
    await waitFor(() => expect(screen.getByText("Asha Verma")).toBeInTheDocument());
  });

  it("creates a participant via the add form (no login/account fields present)", async () => {
    vi.mocked(listParticipants).mockResolvedValue(EMPTY_PAGE);
    vi.mocked(createParticipant).mockResolvedValue({
      id: "part2",
      project_id: "p1",
      name: "Rohit Singh",
      department: null,
      academic_year: null,
      registration_id: null,
      participation_role: "member",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });

    renderWithClient(<ParticipantsPanel projectId="p1" />);
    await waitFor(() => expect(screen.getByText("No participants yet")).toBeInTheDocument());

    // jsdom doesn't implement <dialog> semantics, so the modal's content is
    // always present in the tree — the visible trigger button is the first match.
    act(() => {
      screen.getAllByText("Add participant")[0].click();
    });
    // Confirms the create form never exposes phone/password/login fields —
    // students never get an account.
    expect(screen.queryByLabelText(/phone/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/password/i)).not.toBeInTheDocument();

    const nameInput = screen.getByLabelText("Name") as HTMLInputElement;
    nameInput.value = "Rohit Singh";

    const form = nameInput.closest("form")!;
    act(() => {
      form.requestSubmit();
    });

    await waitFor(() => expect(createParticipant).toHaveBeenCalled());
    const [, payload] = vi.mocked(createParticipant).mock.calls[0];
    expect(payload.name).toBe("Rohit Singh");
  });
});
