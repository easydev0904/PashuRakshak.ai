import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { caseService } from "@/services/caseService";
import type { CaseClinicalUpdateInput, CaseUpdateInput } from "@/services/caseService";

export const caseKeys = {
  forAnimal: (animalId: string) => ["cases", "animal", animalId] as const,
  detail: (caseId: string) => ["cases", "detail", caseId] as const,
};

export function useCasesForAnimal(animalId: string | undefined) {
  return useQuery({
    queryKey: caseKeys.forAnimal(animalId ?? ""),
    queryFn: () => caseService.listForAnimal(animalId!),
    enabled: !!animalId,
  });
}

export function useCase(caseId: string | undefined) {
  return useQuery({
    queryKey: caseKeys.detail(caseId ?? ""),
    queryFn: () => caseService.get(caseId!),
    enabled: !!caseId,
  });
}

export function useUpdateCaseClinical(caseId: string, animalId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CaseClinicalUpdateInput) => caseService.updateClinical(caseId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.detail(caseId) });
      if (animalId) queryClient.invalidateQueries({ queryKey: caseKeys.forAnimal(animalId) });
    },
  });
}

export function useAddCaseUpdate(caseId: string, animalId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CaseUpdateInput) => caseService.addUpdate(caseId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.detail(caseId) });
      if (animalId) queryClient.invalidateQueries({ queryKey: caseKeys.forAnimal(animalId) });
    },
  });
}
