import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { animalService } from "@/services/animalService";
import type { AnimalInput } from "@/services/animalService";
import type { ObservationInput } from "@/types/api";

export const animalKeys = {
  all: ["animals"] as const,
  list: (farmId?: string) => ["animals", "list", farmId ?? "all"] as const,
  detail: (id: string) => ["animals", "detail", id] as const,
  observations: (id: string) => ["animals", id, "observations"] as const,
};

export function useAnimals(farmId?: string) {
  return useQuery({
    queryKey: animalKeys.list(farmId),
    queryFn: () => animalService.list(farmId),
  });
}

export function useAnimal(animalId: string | undefined) {
  return useQuery({
    queryKey: animalKeys.detail(animalId ?? ""),
    queryFn: () => animalService.get(animalId!),
    enabled: !!animalId,
  });
}

export function useCreateAnimal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AnimalInput) => animalService.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: animalKeys.all }),
  });
}

export function useObservations(animalId: string | undefined) {
  return useQuery({
    queryKey: animalKeys.observations(animalId ?? ""),
    queryFn: () => animalService.listObservations(animalId!),
    enabled: !!animalId,
  });
}

export function useSubmitObservation(animalId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ObservationInput) => animalService.submitObservation(animalId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: animalKeys.observations(animalId) });
      queryClient.invalidateQueries({ queryKey: animalKeys.detail(animalId) });
      queryClient.invalidateQueries({ queryKey: animalKeys.all });
    },
  });
}
