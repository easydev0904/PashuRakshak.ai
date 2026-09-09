import { apiClient } from "@/api/client";
import type { Farm } from "@/types/api";

export interface FarmInput {
  name: string;
  village?: string;
  district?: string;
  state?: string;
  latitude?: number;
  longitude?: number;
}

export interface VaccinationDue {
  id: string;
  animal_id: string;
  animal_tag_id: string;
  vaccine_name: string;
  dose_date?: string | null;
  due_date?: string | null;
  administered_by?: string | null;
  evidence_url?: string | null;
  created_at: string;
}

export const farmService = {
  list: () => apiClient.get<Farm[]>("/farms").then((r) => r.data),
  create: (payload: FarmInput) => apiClient.post<Farm>("/farms", payload).then((r) => r.data),
  vaccinationsDue: (farmId: string) =>
    apiClient
      .get<VaccinationDue[]>(`/farms/${farmId}/vaccinations-due`)
      .then((r) => r.data),
};
