import { CalendarClock, ClipboardList, Syringe } from "lucide-react";
import { useTranslation } from "react-i18next";

import { RiskBadge } from "@/components/shared/RiskBadge";
import { Card, CardContent } from "@/components/ui/card";
import type { ObservationWithRisk, RiskAssessment, VaccinationRecord } from "@/types/api";

type TimelineEntry =
  | {
      kind: "observation";
      date: string;
      observation: ObservationWithRisk;
      risk?: RiskAssessment | null;
    }
  | { kind: "vaccination"; date: string; vaccination: VaccinationRecord };

export function AnimalTimeline({
  observations,
  vaccinations,
}: {
  observations: ObservationWithRisk[];
  vaccinations: VaccinationRecord[];
}) {
  const { t } = useTranslation();

  const entries: TimelineEntry[] = [
    ...observations.map((obs) => ({
      kind: "observation" as const,
      date: obs.observed_at,
      observation: obs,
      risk: obs.risk_assessment,
    })),
    ...vaccinations
      .filter((v) => v.dose_date)
      .map((v) => ({ kind: "vaccination" as const, date: v.dose_date as string, vaccination: v })),
  ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("animal.noHistory")}</p>;
  }

  return (
    <ol className="flex flex-col gap-3">
      {entries.map((entry, idx) => (
        <li key={idx}>
          <Card>
            <CardContent className="flex items-start gap-3 p-4">
              <div className="mt-0.5 shrink-0 text-muted-foreground">
                {entry.kind === "observation" ? (
                  <ClipboardList className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Syringe className="h-5 w-5" aria-hidden="true" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">
                    {entry.kind === "observation"
                      ? t("observation.timelineLabel")
                      : entry.vaccination.vaccine_name}
                  </p>
                  {entry.kind === "observation" && entry.risk && (
                    <RiskBadge band={entry.risk.risk_band} />
                  )}
                </div>
                <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                  <CalendarClock className="h-3 w-3" aria-hidden="true" />
                  {new Date(entry.date).toLocaleString()}
                </p>
                {entry.kind === "observation" && entry.risk && entry.risk.top_factors.length > 0 && (
                  <ul className="mt-2 list-inside list-disc text-xs text-muted-foreground">
                    {entry.risk.top_factors.slice(0, 3).map((factor) => (
                      <li key={factor.rule}>{factor.reason}</li>
                    ))}
                  </ul>
                )}
              </div>
            </CardContent>
          </Card>
        </li>
      ))}
    </ol>
  );
}
