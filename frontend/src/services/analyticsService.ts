import { apiClient } from "@/api/client";
import type { FarmTrendsResponse } from "@/types/api";

export const analyticsService = {
  farmTrends: (farmId: string) =>
    apiClient
      .get<FarmTrendsResponse>("/analytics/farm-trends", { params: { farm_id: farmId } })
      .then((r) => r.data),
};
