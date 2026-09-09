import { AlertTriangle, CheckCircle2, TriangleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Badge } from "@/components/ui/badge";
import type { RiskBand } from "@/types/api";

const ICONS: Record<RiskBand, typeof CheckCircle2> = {
  low: CheckCircle2,
  medium: TriangleAlert,
  high: AlertTriangle,
};

export function RiskBadge({ band, className }: { band: RiskBand; className?: string }) {
  const { t } = useTranslation();
  const Icon = ICONS[band];
  return (
    <Badge variant={band} className={className}>
      <Icon className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
      {t(`riskResult.${band}`)}
    </Badge>
  );
}
