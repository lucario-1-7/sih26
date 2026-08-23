import { apiClient } from './client';

export interface AdministrativeArea {
  id: string;
  name: string;
  level: string;
  lgd_code: string | null;
  parent_id: string | null;
}

interface PaginatedAreas {
  items: AdministrativeArea[];
  next_cursor: string | null;
}

/**
 * The backend is authoritative for which administrative_area_id values a
 * challenge may reference — there is no client-side geocoding or pincode
 * lookup. This is the same reference-data endpoint the Flutter Citizen app
 * and the organizational portal both resolve a location against.
 */
export const administrativeAreaApi = {
  async list(search?: string): Promise<AdministrativeArea[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    const res = await apiClient<PaginatedAreas>(`/administrative-areas${query}`);
    return res.items;
  },
};
