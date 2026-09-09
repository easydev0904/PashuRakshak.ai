import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { vaccinationService } from "@/services/vaccinationService";
import type { VaccinationInput } from "@/services/vaccinationService";

export const vaccinationKeys = {
  forAnimal: (animalId: string) => ["vaccinations", animalId] as const,
};

export function useVaccinations(animalId: string | undefined) {
  return useQuery({
    queryKey: vaccinationKeys.forAnimal(animalId ?? ""),
    queryFn: () => vaccinationService.listForAnimal(animalId!),
    enabled: !!animalId,
  });
}

export function useAddVaccination(animalId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: VaccinationInput) => vaccinationService.create(animalId, payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: vaccinationKeys.forAnimal(animalId) }),
  });
}
