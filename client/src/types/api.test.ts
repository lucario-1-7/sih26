import { describe, expect, it } from "vitest";

import { PROJECT_STATUS_TRANSITIONS } from "@/types/api";
import type { ProjectStatus } from "@/types/api";

describe("PROJECT_STATUS_TRANSITIONS", () => {
  it("cannot skip proposed -> active directly", () => {
    expect(PROJECT_STATUS_TRANSITIONS.proposed).not.toContain("active");
  });

  it("proposed can go to accepted or cancelled", () => {
    expect(PROJECT_STATUS_TRANSITIONS.proposed).toEqual(["accepted", "cancelled"]);
  });

  it("completed and cancelled are terminal", () => {
    expect(PROJECT_STATUS_TRANSITIONS.completed).toEqual([]);
    expect(PROJECT_STATUS_TRANSITIONS.cancelled).toEqual([]);
  });

  it("every status has a defined (possibly empty) transition list", () => {
    const statuses: ProjectStatus[] = ["proposed", "accepted", "active", "on_hold", "completed", "cancelled"];
    for (const status of statuses) {
      expect(PROJECT_STATUS_TRANSITIONS[status]).toBeDefined();
    }
  });
});
