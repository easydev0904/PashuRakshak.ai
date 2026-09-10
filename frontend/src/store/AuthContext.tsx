import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { tokenStorage } from "@/api/client";
import { authService } from "@/services/authService";
import type { LoginRequest, User } from "@/types/api";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (payload: LoginRequest) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const USER_CACHE_KEY = "pashurakshak.user";

function readCachedUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_CACHE_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(readCachedUser);
  const [isLoading, setIsLoading] = useState(() => !!tokenStorage.getAccessToken());

  useEffect(() => {
    const token = tokenStorage.getAccessToken();
    if (!token) return;
    authService
      .me()
      .then((freshUser) => {
        setUser(freshUser);
        localStorage.setItem(USER_CACHE_KEY, JSON.stringify(freshUser));
      })
      .catch(() => {
        tokenStorage.clear();
        localStorage.removeItem(USER_CACHE_KEY);
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (payload: LoginRequest) => {
    const result = await authService.login(payload);
    tokenStorage.setTokens(result.access_token, result.refresh_token);
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(result.user));
    setUser(result.user);
    return result.user;
  }, []);

  const logout = useCallback(() => {
    tokenStorage.clear();
    localStorage.removeItem(USER_CACHE_KEY);
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, isLoading, login, logout }), [user, isLoading, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components -- co-located hook is intentional
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
