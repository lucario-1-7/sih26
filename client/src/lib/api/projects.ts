import { apiFetch } from "@/lib/api/client";
import type {
  PaginatedResponse,
  ProjectCreateInput,
  ProjectResponse,
  ProjectStatus,
  ProjectUpdateInput,
} from "@/types/api";

export function listProjects(params: {
  cursor?: string | null;
  limit?: number;
  status?: ProjectStatus;
  cluster_id?: string;
}): Promise<PaginatedResponse<ProjectResponse>> {
  return apiFetch<PaginatedResponse<ProjectResponse>>("/projects", {
    query: {
      cursor: params.cursor ?? undefined,
      limit: params.limit ?? 20,
      status: params.status,
      cluster_id: params.cluster_id,
    },
  });
}

export function getProject(projectId: string): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${projectId}`);
}

export function createProject(data: ProjectCreateInput): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>("/projects", { method: "POST", body: data });
}

export function updateProject(projectId: string, data: ProjectUpdateInput): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${projectId}`, { method: "PATCH", body: data });
}
