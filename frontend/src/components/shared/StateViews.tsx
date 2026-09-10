import { Loader2, WifiOff } from "lucide-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";

export function LoadingState({ label }: { label?: string }) {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
      <Loader2 className="h-8 w-8 animate-spin text-primary" aria-hidden="true" />
      <p>{label ?? t("common.loading")}</p>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-border bg-card py-16 text-center">
      <p className="max-w-sm text-muted-foreground">{message ?? t("common.unableToLoad")}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          {t("common.retry")}
        </Button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-border bg-card/50 py-16 text-center">
      <p className="text-base font-medium text-foreground">{title}</p>
      {description && <p className="max-w-sm text-sm text-muted-foreground">{description}</p>}
      {action}
    </div>
  );
}

export function OfflineBanner() {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-2 rounded-xl bg-secondary/20 px-4 py-2 text-sm text-secondary-foreground">
      <WifiOff className="h-4 w-4" aria-hidden="true" />
      {t("common.offline")}
    </div>
  );
}
