import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { AlertRow } from "@/components/shared/AlertRow";
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Card, CardContent } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { useAlerts } from "@/hooks/useAlerts";
import { useFarms } from "@/hooks/useFarms";

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs text-muted-foreground">{label}</p>
      </CardContent>
    </Card>
  );
}

export function VetDashboardPage() {
  const { t } = useTranslation();
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [farmFilter, setFarmFilter] = useState("");

  const farmsQuery = useFarms();
  const alertsQuery = useAlerts({
    status: statusFilter || undefined,
    priority: priorityFilter || undefined,
    farm_id: farmFilter || undefined,
  });

  const stats = useMemo(() => {
    const alerts = alertsQuery.data ?? [];
    return {
      totalActive: alerts.filter((a) => a.status !== "resolved").length,
      high: alerts.filter((a) => a.priority === "high" && a.status !== "resolved").length,
      medium: alerts.filter((a) => a.priority === "medium" && a.status !== "resolved").length,
      followUps: alerts.filter((a) => a.status === "in_review").length,
      resolved: alerts.filter((a) => a.status === "resolved").length,
    };
  }, [alertsQuery.data]);

  if (alertsQuery.isLoading) return <LoadingState />;
  if (alertsQuery.isError) return <ErrorState onRetry={() => alertsQuery.refetch()} />;

  const alerts = alertsQuery.data ?? [];

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <h1 className="text-2xl font-bold">{t("vetDashboard.title")}</h1>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label={t("vetDashboard.totalActive")} value={stats.totalActive} />
        <StatCard label={t("vetDashboard.highPriority")} value={stats.high} />
        <StatCard label={t("vetDashboard.mediumPriority")} value={stats.medium} />
        <StatCard label={t("vetDashboard.followUpsDue")} value={stats.followUps} />
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-auto"
        >
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="assigned">Assigned</option>
          <option value="in_review">In review</option>
          <option value="resolved">Resolved</option>
        </Select>
        <Select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="w-auto"
        >
          <option value="">All priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </Select>
        {farmsQuery.data && farmsQuery.data.length > 0 && (
          <Select
            value={farmFilter}
            onChange={(e) => setFarmFilter(e.target.value)}
            className="w-auto"
          >
            <option value="">All farms</option>
            {farmsQuery.data.map((farm) => (
              <option key={farm.id} value={farm.id}>
                {farm.name}
              </option>
            ))}
          </Select>
        )}
      </div>

      {alerts.length === 0 ? (
        <EmptyState title={t("vetDashboard.noAlerts")} />
      ) : (
        <div className="flex flex-col gap-3">
          {alerts.map((alert) => (
            <AlertRow key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </div>
  );
}
