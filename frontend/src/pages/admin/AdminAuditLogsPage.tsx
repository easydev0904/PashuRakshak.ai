import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuditLogs } from "@/hooks/useAuditLogs";

export function AdminAuditLogsPage() {
  const { t } = useTranslation();
  const [entityType, setEntityType] = useState("");
  const logsQuery = useAuditLogs({ entity_type: entityType || undefined, limit: 100 });

  if (logsQuery.isLoading) return <LoadingState />;
  if (logsQuery.isError) return <ErrorState onRetry={() => logsQuery.refetch()} />;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-bold">{t("admin.auditTitle")}</h1>

      <Input
        placeholder="Filter by entity type (e.g. animal, alert, case, user)"
        value={entityType}
        onChange={(e) => setEntityType(e.target.value)}
        className="max-w-sm"
      />

      <div className="overflow-x-auto">
        <div className="flex min-w-[600px] flex-col gap-2">
          {(logsQuery.data ?? []).map((log) => (
            <Card key={log.id}>
              <CardContent className="flex items-center gap-4 p-3 text-sm">
                <span className="w-40 shrink-0 text-muted-foreground">
                  {new Date(log.created_at).toLocaleString()}
                </span>
                <span className="w-28 shrink-0 font-medium capitalize">{log.entity_type}</span>
                <span className="w-28 shrink-0 capitalize">{log.action}</span>
                <span className="flex-1 truncate text-muted-foreground">
                  {JSON.stringify(log.metadata_json)}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
