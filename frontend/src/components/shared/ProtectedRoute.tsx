import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { LoadingState } from "@/components/shared/StateViews";
import { useAuth } from "@/store/AuthContext";
import type { UserRole } from "@/types/api";

export function ProtectedRoute({
  roles,
  children,
}: {
  roles?: UserRole[];
  children: ReactNode;
}) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <LoadingState />;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) {
    return <Navigate to={homeRouteForRole(user.role)} replace />;
  }
  return <>{children}</>;
}

// eslint-disable-next-line react-refresh/only-export-components -- co-located helper is intentional
export function homeRouteForRole(role: UserRole): string {
  if (role === "farmer") return "/farmer/dashboard";
  if (role === "veterinarian") return "/vet/dashboard";
  return "/admin/users";
}
