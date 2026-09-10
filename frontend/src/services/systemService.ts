import { apiClient } from "@/api/client";

export interface SystemHealth {
  status: string;
  environment: string;
  total_users?: number | null;
  total_farms?: number | null;
  total_animals?: number | null;
}

export const systemService = {
  health: () => apiClient.get<SystemHealth>("/analytics/system-health").then((r) => r.data),
};
