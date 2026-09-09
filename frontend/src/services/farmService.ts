import { apiClient } from "@/api/client";
import type { Farm } from "@/types/api";

export interface FarmInput {
  name: string;
  village?: string;
  district?: string;
  state?: string;
  latitude?: number;
  longitude?: number;
}

export const farmService = {
  list: () => apiClient.get<Farm[]>("/farms").then((r) => r.data),
  create: (payload: FarmInput) => apiClient.post<Farm>("/farms", payload).then((r) => r.data),
};
