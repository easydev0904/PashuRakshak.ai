import { useQuery } from "@tanstack/react-query";

import { analyticsService } from "@/services/analyticsService";

export function useFarmTrends(farmId: string | undefined) {
  return useQuery({
    queryKey: ["analytics", "farm-trends", farmId],
    queryFn: () => analyticsService.farmTrends(farmId!),
    enabled: !!farmId,
  });
}
