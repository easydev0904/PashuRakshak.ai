import { apiClient } from "@/api/client";
import type { Alert, AlertDetail, AlertReviewAction } from "@/types/api";

export interface AlertFilters {
  status?: string;
  priority?: string;
  farm_id?: string;
  assigned_vet_id?: string;
}

export const alertService = {
  list: (filters: AlertFilters = {}) =>
    apiClient.get<Alert[]>("/alerts", { params: filters }).then((r) => r.data),
  get: (alertId: string) => apiClient.get<AlertDetail>(`/alerts/${alertId}`).then((r) => r.data),
  review: (alertId: string, action: AlertReviewAction) =>
    apiClient.post<Alert>(`/alerts/${alertId}/review`, action).then((r) => r.data),
};
