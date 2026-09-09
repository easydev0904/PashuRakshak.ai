import { useState } from "react";
import { useTranslation } from "react-i18next";

import { EmptyState, ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Card, CardContent } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { useFarms } from "@/hooks/useFarms";
import { useFarmTrends } from "@/hooks/useAnalytics";
import { useAuth } from "@/store/AuthContext";

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

export function AnalyticsPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const farmsQuery = useFarms();
  const [selectedFarmId, setSelectedFarmId] = useState<string>("");

  const farms = farmsQuery.data ?? [];
  const activeFarmId = selectedFarmId || farms[0]?.id;
  const trendsQuery = useFarmTrends(activeFarmId);

  if (farmsQuery.isLoading) return <LoadingState />;
  if (farms.length === 0) {
    return <EmptyState title="No farms yet" description="Trends will appear once a farm has observations." />;
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("analytics.title")}</h1>
        {user?.role !== "farmer" && farms.length > 1 && (
          <Select
            value={activeFarmId}
            onChange={(e) => setSelectedFarmId(e.target.value)}
            className="w-auto"
          >
            {farms.map((farm) => (
              <option key={farm.id} value={farm.id}>
                {farm.name}
              </option>
            ))}
          </Select>
        )}
      </div>

      {trendsQuery.isLoading ? (
        <LoadingState />
      ) : trendsQuery.isError || !trendsQuery.data ? (
        <ErrorState onRetry={() => trendsQuery.refetch()} />
      ) : (
        <>
          <p className="text-lg font-medium">{trendsQuery.data.farm_name}</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard label={t("analytics.totalAnimals")} value={trendsQuery.data.total_animals} />
            <StatCard
              label={t("analytics.totalObservations")}
              value={trendsQuery.data.total_observations}
            />
            <StatCard label={t("analytics.openAlerts")} value={trendsQuery.data.open_alerts} />
            <StatCard
              label={t("analytics.vaccinationsDue")}
              value={trendsQuery.data.vaccinations_due}
            />
          </div>

          <Card>
            <CardContent className="p-5">
              <p className="mb-3 text-sm font-medium">Daily trend (last 30 days)</p>
              {trendsQuery.data.daily_trend.length === 0 ? (
                <p className="text-sm text-muted-foreground">No observations in this period.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[500px] text-left text-sm">
                    <thead>
                      <tr className="text-muted-foreground">
                        <th className="pb-2 pr-4">Date</th>
                        <th className="pb-2 pr-4">Observations</th>
                        <th className="pb-2 pr-4 text-[hsl(var(--risk-low))]">Low</th>
                        <th className="pb-2 pr-4 text-[hsl(var(--risk-medium))]">Medium</th>
                        <th className="pb-2 text-[hsl(var(--risk-high))]">High</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trendsQuery.data.daily_trend.map((point) => (
                        <tr key={point.date} className="border-t border-border">
                          <td className="py-1.5 pr-4">{point.date}</td>
                          <td className="py-1.5 pr-4">{point.observation_count}</td>
                          <td className="py-1.5 pr-4">{point.low_risk_count}</td>
                          <td className="py-1.5 pr-4">{point.medium_risk_count}</td>
                          <td className="py-1.5">{point.high_risk_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          <p className="text-xs text-muted-foreground">{trendsQuery.data.note}</p>
        </>
      )}
    </div>
  );
}
