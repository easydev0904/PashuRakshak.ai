import { CloudOff } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function OfflineSavedView({ animalId }: { animalId: string }) {
  const { t } = useTranslation();

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-4">
      <Card>
        <CardContent className="flex flex-col items-center gap-3 p-8 text-center">
          <CloudOff className="h-10 w-10 text-secondary-foreground" aria-hidden="true" />
          <p className="text-lg font-semibold">{t("common.offline")}</p>
          <p className="text-muted-foreground">{t("common.savedOffline")}</p>
        </CardContent>
      </Card>
      <Button variant="outline" size="lg" asChild>
        <Link to={`/farmer/animals/${animalId}`}>{t("riskResult.backToDashboard")}</Link>
      </Button>
    </div>
  );
}
