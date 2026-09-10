import { Beef, Clock } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { resolveMediaUrl } from "@/api/client";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { AnimalSummary } from "@/types/api";

export function AnimalCard({ animal }: { animal: AnimalSummary }) {
  const { t } = useTranslation();

  return (
    <Link to={`/farmer/animals/${animal.id}`} className="block">
      <Card className="transition-shadow hover:shadow-md">
        <CardContent className="flex items-center gap-4 p-4">
          {animal.photo_url ? (
            <img
              src={resolveMediaUrl(animal.photo_url)}
              alt=""
              className="h-12 w-12 shrink-0 rounded-full object-cover"
            />
          ) : (
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Beef className="h-6 w-6" aria-hidden="true" />
            </div>
          )}
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="font-semibold">{animal.tag_id}</p>
              {animal.needs_checkin_today && (
                <Badge variant="secondary" className="text-[10px]">
                  <Clock className="mr-1 h-3 w-3" />
                  {t("animal.checkinDue")}
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">{t(`animal.${animal.species}`)}</p>
          </div>
          {animal.last_risk_band && <RiskBadge band={animal.last_risk_band} />}
        </CardContent>
      </Card>
    </Link>
  );
}
