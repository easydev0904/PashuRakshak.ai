import { Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/components/shared/ProtectedRoute";
import { LoginPage } from "@/pages/auth/LoginPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { RootRedirect } from "@/pages/RootRedirect";
import { AdminAuditLogsPage } from "@/pages/admin/AdminAuditLogsPage";
import { AdminEducationPage } from "@/pages/admin/AdminEducationPage";
import { AdminFarmsPage } from "@/pages/admin/AdminFarmsPage";
import { AdminSystemPage } from "@/pages/admin/AdminSystemPage";
import { AdminUsersPage } from "@/pages/admin/AdminUsersPage";
import { AnimalProfilePage } from "@/pages/farmer/AnimalProfilePage";
import { AnimalRegisterPage } from "@/pages/farmer/AnimalRegisterPage";
import { AnimalsListPage } from "@/pages/farmer/AnimalsListPage";
import { FarmerDashboardPage } from "@/pages/farmer/FarmerDashboardPage";
import { ObservationFormPage } from "@/pages/farmer/ObservationFormPage";
import { AnalyticsPage } from "@/pages/shared/AnalyticsPage";
import { PreventionLibraryPage } from "@/pages/shared/PreventionLibraryPage";
import { AlertDetailPage } from "@/pages/vet/AlertDetailPage";
import { VetDashboardPage } from "@/pages/vet/VetDashboardPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<AppShell />}>
        <Route
          path="/farmer/dashboard"
          element={
            <ProtectedRoute roles={["farmer"]}>
              <FarmerDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farmer/animals"
          element={
            <ProtectedRoute roles={["farmer"]}>
              <AnimalsListPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farmer/animals/new"
          element={
            <ProtectedRoute roles={["farmer"]}>
              <AnimalRegisterPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farmer/animals/:animalId"
          element={
            <ProtectedRoute roles={["farmer", "veterinarian", "admin"]}>
              <AnimalProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farmer/animals/:animalId/observe"
          element={
            <ProtectedRoute roles={["farmer"]}>
              <ObservationFormPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/vet/dashboard"
          element={
            <ProtectedRoute roles={["veterinarian", "admin"]}>
              <VetDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/vet/alerts/:alertId"
          element={
            <ProtectedRoute roles={["veterinarian", "admin"]}>
              <AlertDetailPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/users"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/farms"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminFarmsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/education"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminEducationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/audit-logs"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminAuditLogsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/system"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminSystemPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/prevention"
          element={
            <ProtectedRoute>
              <PreventionLibraryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute roles={["farmer", "veterinarian", "admin"]}>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="/" element={<RootRedirect />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
