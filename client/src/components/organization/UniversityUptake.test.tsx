import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { UniversityUptake, UniversityUptakeInline } from "@/components/organization/UniversityUptake";
import type { OrganizationSummary } from "@/types/api";

const REAL_UNIVERSITY: OrganizationSummary = {
  id: "org-42",
  name: "Indian Institute of Technology Dhanbad",
  type: "university",
};

describe("UniversityUptake", () => {
  it("displays the actual university name from the API response, not a hardcoded value", () => {
    render(<UniversityUptake university={REAL_UNIVERSITY} />);
    expect(screen.getByText("Indian Institute of Technology Dhanbad")).toBeInTheDocument();
  });

  it("shows the correct empty state when no university has taken up the project", () => {
    render(<UniversityUptake university={null} />);
    expect(screen.getByText("Not yet taken up by a university")).toBeInTheDocument();
    expect(screen.queryByText("Indian Institute of Technology Dhanbad")).not.toBeInTheDocument();
  });

  it("re-renders with a different real university when the prop changes (proves the value is driven by data, not fixed markup)", () => {
    const { rerender } = render(<UniversityUptake university={REAL_UNIVERSITY} />);
    expect(screen.getByText("Indian Institute of Technology Dhanbad")).toBeInTheDocument();

    const otherUniversity: OrganizationSummary = { id: "org-99", name: "VIT Chennai", type: "university" };
    rerender(<UniversityUptake university={otherUniversity} />);
    expect(screen.getByText("VIT Chennai")).toBeInTheDocument();
    expect(screen.queryByText("Indian Institute of Technology Dhanbad")).not.toBeInTheDocument();
  });
});

describe("UniversityUptakeInline", () => {
  it("shows the real university name inline when present", () => {
    render(<UniversityUptakeInline university={REAL_UNIVERSITY} />);
    expect(screen.getByText("Taken up by Indian Institute of Technology Dhanbad")).toBeInTheDocument();
  });

  it("shows the correct empty state inline when absent", () => {
    render(<UniversityUptakeInline university={null} />);
    expect(screen.getByText("Not yet taken up")).toBeInTheDocument();
  });
});
