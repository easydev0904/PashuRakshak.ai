import { apiClient } from "@/api/client";
import type { EducationCategory, EducationContent, Language } from "@/types/api";

export interface EducationFilters {
  language?: Language;
  category?: EducationCategory;
}

export interface EducationContentInput {
  category: EducationCategory;
  title: string;
  language: Language;
  body: string;
  audience?: "farmer" | "veterinarian" | "all";
  is_published?: boolean;
}

export const educationService = {
  list: (filters: EducationFilters = {}) =>
    apiClient.get<EducationContent[]>("/education", { params: filters }).then((r) => r.data),
  create: (payload: EducationContentInput) =>
    apiClient.post<EducationContent>("/education", payload).then((r) => r.data),
  update: (contentId: string, payload: Partial<EducationContentInput>) =>
    apiClient.patch<EducationContent>(`/education/${contentId}`, payload).then((r) => r.data),
};
