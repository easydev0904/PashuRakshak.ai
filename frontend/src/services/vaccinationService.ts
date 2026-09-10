import { apiClient } from "@/api/client";
import type { VaccinationRecord } from "@/types/api";

export interface VaccinationInput {
  vaccine_name: string;
  dose_date?: string;
  due_date?: string;
  evidence_url?: string;
}

export const vaccinationService = {
  listForAnimal: (animalId: string) =>
    apiClient.get<VaccinationRecord[]>(`/animals/${animalId}/vaccinations`).then((r) => r.data),
  create: (animalId: string, payload: VaccinationInput) =>
    apiClient
      .post<VaccinationRecord>(`/animals/${animalId}/vaccinations`, payload)
      .then((r) => r.data),
};
