import { apiFetch } from "@/lib/api/client";
import type { PaginatedResponse, ThemeCreateInput, ThemeResponse, ThemeUpdateInput } from "@/types/api";

export function listThemes(params: { cursor?: string; limit?: number } = {}): Promise<PaginatedResponse<ThemeResponse>> {
  return apiFetch<PaginatedResponse<ThemeResponse>>("/themes", {
    query: { cursor: params.cursor, limit: params.limit ?? 20 },
  });
}

export function createTheme(data: ThemeCreateInput): Promise<ThemeResponse> {
  return apiFetch<ThemeResponse>("/themes", { method: "POST", body: data });
}

export function updateTheme(themeId: string, data: ThemeUpdateInput): Promise<ThemeResponse> {
  return apiFetch<ThemeResponse>(`/themes/${themeId}`, { method: "PATCH", body: data });
}
