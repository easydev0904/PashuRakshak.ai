import { apiClient } from "@/api/client";
import type {
  Animal,
  AnimalSummary,
  ObservationInput,
  ObservationResult,
  ObservationWithRisk,
  Sex,
  Species,
} from "@/types/api";

export interface AnimalInput {
  farm_id: string;
  tag_id: string;
  species: Species;
  breed?: string;
  sex: Sex;
  dob?: string;
  notes?: string;
  photo_url?: string;
}

export const animalService = {
  list: (farmId?: string) =>
    apiClient
      .get<AnimalSummary[]>("/animals", { params: farmId ? { farm_id: farmId } : undefined })
      .then((r) => r.data),
  get: (animalId: string) =>
    apiClient.get<AnimalSummary>(`/animals/${animalId}`).then((r) => r.data),
  create: (payload: AnimalInput) =>
    apiClient.post<Animal>("/animals", payload).then((r) => r.data),
  listObservations: (animalId: string) =>
    apiClient
      .get<ObservationWithRisk[]>(`/animals/${animalId}/observations`)
      .then((r) => r.data),
  submitObservation: (animalId: string, payload: ObservationInput) =>
    apiClient
      .post<ObservationResult>(`/animals/${animalId}/observations`, payload)
      .then((r) => r.data),
};
