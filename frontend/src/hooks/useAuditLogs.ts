import { useQuery } from "@tanstack/react-query";

import { auditLogService } from "@/services/auditLogService";
import type { AuditLogFilters } from "@/services/auditLogService";

export function useAuditLogs(filters: AuditLogFilters = {}) {
  return useQuery({
    queryKey: ["audit-logs", filters],
    queryFn: () => auditLogService.list(filters),
  });
}
