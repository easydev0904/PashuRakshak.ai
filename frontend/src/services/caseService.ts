import { apiClient } from "@/api/client";
import type { Case, CaseStatus } from "@/types/api";

export interface CaseClinicalUpdateInput {
  status?: CaseStatus;
  suspected_condition?: string;
  confirmed_condition?: string;
  confirmation_basis?: string;
}

export interface CaseUpdateInput {
  note: string;
  next_follow_up_at?: string;
}

export const caseService = {
  listForAnimal: (animalId: string) =>
    apiClient.get<Case[]>(`/animals/${animalId}/cases`).then((r) => r.data),
  get: (caseId: string) => apiClient.get<Case>(`/cases/${caseId}`).then((r) => r.data),
  updateClinical: (caseId: string, payload: CaseClinicalUpdateInput) =>
    apiClient.patch<Case>(`/cases/${caseId}`, payload).then((r) => r.data),
  addUpdate: (caseId: string, payload: CaseUpdateInput) =>
    apiClient.post<Case>(`/cases/${caseId}/updates`, payload).then((r) => r.data),
};
