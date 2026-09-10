import { Navigate } from "react-router-dom";

import { LoadingState } from "@/components/shared/StateViews";
import { homeRouteForRole } from "@/components/shared/ProtectedRoute";
import { useAuth } from "@/store/AuthContext";

export function RootRedirect() {
  const { user, isLoading } = useAuth();
  if (isLoading) return <LoadingState />;
  return <Navigate to={user ? homeRouteForRole(user.role) : "/login"} replace />;
}
