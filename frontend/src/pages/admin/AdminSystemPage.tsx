import { useQuery } from "@tanstack/react-query";
import { CheckCircle2 } from "lucide-react";

import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { systemService } from "@/services/systemService";

function StatCard({ label, value }: { label: string; value: number | null | undefined }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-2xl font-bold">{value ?? "—"}</p>
        <p className="text-xs text-muted-foreground">{label}</p>
      </CardContent>
    </Card>
  );
}

export function AdminSystemPage() {
  const healthQuery = useQuery({
    queryKey: ["system-health"],
    queryFn: systemService.health,
  });

  if (healthQuery.isLoading) return <LoadingState />;
  if (healthQuery.isError || !healthQuery.data) {
    return <ErrorState onRetry={() => healthQuery.refetch()} />;
  }

  const health = healthQuery.data;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <h1 className="text-2xl font-bold">System</h1>

      <Card>
        <CardContent className="flex items-center gap-3 p-5">
          <CheckCircle2 className="h-6 w-6 text-[hsl(var(--risk-low))]" aria-hidden="true" />
          <div>
            <p className="font-medium">Backend is healthy</p>
            <p className="text-sm text-muted-foreground">
              Environment: <Badge variant="outline">{health.environment}</Badge>
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-3 gap-3">
        <StatCard label="Users" value={health.total_users} />
        <StatCard label="Farms" value={health.total_farms} />
        <StatCard label="Animals" value={health.total_animals} />
      </div>
    </div>
  );
}
