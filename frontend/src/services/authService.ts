import { apiClient } from "@/api/client";
import type { LoginRequest, TokenResponse, User } from "@/types/api";

export const authService = {
  login: (payload: LoginRequest) =>
    apiClient.post<TokenResponse>("/auth/login", payload).then((r) => r.data),
  me: () => apiClient.get<User>("/auth/me").then((r) => r.data),
};
