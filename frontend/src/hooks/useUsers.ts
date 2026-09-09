import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { userService } from "@/services/userService";
import type { UserCreateInput, UserFilters, UserUpdateInput } from "@/services/userService";

export const userKeys = {
  list: (filters: UserFilters) => ["users", "list", filters] as const,
};

export function useUsers(filters: UserFilters = {}) {
  return useQuery({ queryKey: userKeys.list(filters), queryFn: () => userService.list(filters) });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserCreateInput) => userService.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: UserUpdateInput }) =>
      userService.update(userId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}
