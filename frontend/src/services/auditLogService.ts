import { apiClient } from "@/api/client";

export interface AuditLogEntry {
  id: string;
  actor_id: string | null;
  entity_type: string;
  entity_id: string | null;
  action: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

export interface AuditLogFilters {
  entity_type?: string;
  action?: string;
  actor_id?: string;
  limit?: number;
}

export const auditLogService = {
  list: (filters: AuditLogFilters = {}) =>
    apiClient.get<AuditLogEntry[]>("/audit-logs", { params: filters }).then((r) => r.data),
};
