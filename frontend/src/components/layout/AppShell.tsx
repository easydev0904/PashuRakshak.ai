import {
  Activity,
  BarChart3,
  LayoutDashboard,
  LogOut,
  Menu,
  PawPrint,
  ShieldAlert,
  Sprout,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, Outlet } from "react-router-dom";

import { LanguageSwitcher } from "@/components/shared/LanguageSwitcher";
import { OfflineBanner } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { cn } from "@/lib/utils";
import { useAuth } from "@/store/AuthContext";

interface NavItem {
  to: string;
  labelKey: string;
  icon: LucideIcon;
}

const NAV_BY_ROLE: Record<string, NavItem[]> = {
  farmer: [
    { to: "/farmer/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard },
    { to: "/farmer/animals", labelKey: "nav.animals", icon: PawPrint },
    { to: "/prevention", labelKey: "nav.prevention", icon: Sprout },
    { to: "/analytics", labelKey: "nav.analytics", icon: BarChart3 },
  ],
  veterinarian: [
    { to: "/vet/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard },
    { to: "/prevention", labelKey: "nav.prevention", icon: Sprout },
    { to: "/analytics", labelKey: "nav.analytics", icon: BarChart3 },
  ],
  admin: [
    { to: "/admin/users", labelKey: "nav.users", icon: LayoutDashboard },
    { to: "/admin/farms", labelKey: "nav.farms", icon: PawPrint },
    { to: "/admin/education", labelKey: "nav.education", icon: Sprout },
    { to: "/admin/audit-logs", labelKey: "nav.auditLogs", icon: ShieldAlert },
    { to: "/admin/system", labelKey: "nav.system", icon: Activity },
  ],
};

export function AppShell() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const isOnline = useOnlineStatus();
  const { pendingCount, isSyncing } = useOfflineSync();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const navItems = user ? NAV_BY_ROLE[user.role] ?? [] : [];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-20 flex items-center justify-between border-b border-border bg-card px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <button
            className="rounded-lg p-2 hover:bg-muted md:hidden"
            aria-label="Toggle navigation"
            onClick={() => setMobileNavOpen((v) => !v)}
          >
            {mobileNavOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <span className="text-lg font-bold text-primary">{t("app.name")}</span>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <LanguageSwitcher />
          {user && (
            <Button variant="ghost" size="sm" onClick={logout} aria-label={t("common.logout")}>
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">{t("common.logout")}</span>
            </Button>
          )}
        </div>
      </header>

      {(!isOnline || pendingCount > 0) && (
        <div className="flex flex-wrap items-center gap-2 px-4 pt-3 sm:px-6">
          {!isOnline && <OfflineBanner />}
          {pendingCount > 0 && (
            <span className="rounded-full bg-secondary/20 px-3 py-1 text-xs font-medium text-secondary-foreground">
              {isSyncing
                ? t("common.syncing")
                : `${pendingCount} ${pendingCount === 1 ? "draft" : "drafts"} waiting to sync`}
            </span>
          )}
        </div>
      )}

      <div className="flex flex-1">
        <nav
          className={cn(
            "w-64 shrink-0 border-r border-border bg-card px-3 py-4 md:block",
            mobileNavOpen
              ? "fixed inset-y-0 left-0 top-[57px] z-10 block h-[calc(100%-57px)] overflow-y-auto"
              : "hidden",
          )}
        >
          <ul className="flex flex-col gap-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  onClick={() => setMobileNavOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      "flex min-h-[48px] items-center gap-3 rounded-xl px-4 py-2 text-sm font-medium",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-foreground hover:bg-muted",
                    )
                  }
                >
                  <item.icon className="h-5 w-5" aria-hidden="true" />
                  {t(item.labelKey)}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <main className="flex-1 px-4 py-6 sm:px-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
