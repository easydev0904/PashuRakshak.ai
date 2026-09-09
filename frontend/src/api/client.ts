import axios, { type AxiosError } from "axios";

import type { ApiErrorBody, TokenResponse } from "@/types/api";

const ACCESS_TOKEN_KEY = "pashurakshak.access_token";
const REFRESH_TOKEN_KEY = "pashurakshak.refresh_token";

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const apiClient = axios.create({ baseURL });

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) return null;
  try {
    const { data } = await axios.post<TokenResponse>(`${baseURL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    tokenStorage.setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    tokenStorage.clear();
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config;
    if (error.response?.status === 401 && original && !("_retried" in original)) {
      (original as typeof original & { _retried: boolean })._retried = true;
      const newToken = await (refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      }));
      if (newToken && original.headers) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(original);
      }
    }
    return Promise.reject(error);
  },
);

/** True when the request never reached the server (offline, DNS, timeout) --
 * as opposed to a real 4xx/5xx the server sent back. Callers use this to
 * decide whether to fall back to an offline draft or show a real error. */
export function isNetworkError(error: unknown): boolean {
  return axios.isAxiosError(error) && !error.response;
}

export function friendlyErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined;
    if (body?.detail) return body.detail;
    if (error.code === "ERR_NETWORK") {
      return "Unable to reach the server. Please check your connection and try again.";
    }
  }
  return fallback;
}
