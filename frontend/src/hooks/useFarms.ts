import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { farmService } from "@/services/farmService";
import type { FarmInput } from "@/services/farmService";

export const farmKeys = {
  all: ["farms"] as const,
};

export function useFarms() {
  return useQuery({ queryKey: farmKeys.all, queryFn: farmService.list });
}

export function useCreateFarm() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: FarmInput) => farmService.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: farmKeys.all }),
  });
}
