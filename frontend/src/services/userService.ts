import { apiClient } from "@/api/client";
import type { Language, User, UserRole } from "@/types/api";

export interface UserFilters {
  role?: UserRole;
}

export interface UserCreateInput {
  name: string;
  email?: string;
  phone?: string;
  role: UserRole;
  language?: Language;
  password: string;
}

export interface UserUpdateInput {
  name?: string;
  language?: Language;
  is_active?: boolean;
}

export const userService = {
  list: (filters: UserFilters = {}) =>
    apiClient.get<User[]>("/users", { params: filters }).then((r) => r.data),
  create: (payload: UserCreateInput) =>
    apiClient.post<User>("/users", payload).then((r) => r.data),
  update: (userId: string, payload: UserUpdateInput) =>
    apiClient.patch<User>(`/users/${userId}`, payload).then((r) => r.data),
};
