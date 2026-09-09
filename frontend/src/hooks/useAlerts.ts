import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { alertService } from "@/services/alertService";
import type { AlertFilters } from "@/services/alertService";
import type { AlertReviewAction } from "@/types/api";

export const alertKeys = {
  all: ["alerts"] as const,
  list: (filters: AlertFilters) => ["alerts", "list", filters] as const,
  detail: (id: string) => ["alerts", "detail", id] as const,
};

export function useAlerts(filters: AlertFilters = {}) {
  return useQuery({
    queryKey: alertKeys.list(filters),
    queryFn: () => alertService.list(filters),
  });
}

export function useAlert(alertId: string | undefined) {
  return useQuery({
    queryKey: alertKeys.detail(alertId ?? ""),
    queryFn: () => alertService.get(alertId!),
    enabled: !!alertId,
  });
}

export function useReviewAlert(alertId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (action: AlertReviewAction) => alertService.review(alertId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.all });
      queryClient.invalidateQueries({ queryKey: alertKeys.detail(alertId) });
    },
  });
}
