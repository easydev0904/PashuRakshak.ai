import { Clock } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { Alert } from "@/types/api";

const PRIORITY_VARIANT: Record<Alert["priority"], "low" | "medium" | "high"> = {
  low: "low",
  medium: "medium",
  high: "high",
};

const STATUS_LABEL: Record<Alert["status"], string> = {
  open: "Open",
  acknowledged: "Acknowledged",
  assigned: "Assigned",
  in_review: "In review",
  resolved: "Resolved",
};

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function AlertRow({ alert }: { alert: Alert }) {
  return (
    <Link to={`/vet/alerts/${alert.id}`} className="block">
      <Card className="transition-shadow hover:shadow-md">
        <CardContent className="flex items-center gap-4 p-4">
          <Badge variant={PRIORITY_VARIANT[alert.priority]} className="uppercase">
            {alert.priority}
          </Badge>
          <div className="flex-1">
            <p className="text-sm font-medium">{STATUS_LABEL[alert.status]}</p>
            <p className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" aria-hidden="true" />
              {timeAgo(alert.created_at)}
            </p>
          </div>
          <div
            className={cn(
              "h-2 w-2 shrink-0 rounded-full",
              alert.status === "resolved" ? "bg-muted-foreground/40" : "bg-primary",
            )}
          />
        </CardContent>
      </Card>
    </Link>
  );
}
