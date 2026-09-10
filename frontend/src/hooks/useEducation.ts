import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { educationService } from "@/services/educationService";
import type { EducationContentInput, EducationFilters } from "@/services/educationService";

export function useEducationContent(filters: EducationFilters = {}) {
  return useQuery({
    queryKey: ["education", "list", filters],
    queryFn: () => educationService.list(filters),
  });
}

export function useAllEducationContentForAdmin() {
  return useQuery({
    queryKey: ["education", "admin-all"],
    queryFn: () => educationService.listAllForAdmin(),
  });
}

export function useCreateEducationContent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: EducationContentInput) => educationService.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["education"] }),
  });
}

export function useUpdateEducationContent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      contentId,
      payload,
    }: {
      contentId: string;
      payload: Partial<EducationContentInput>;
    }) => educationService.update(contentId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["education"] }),
  });
}
