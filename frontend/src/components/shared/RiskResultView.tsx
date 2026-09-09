import { Phone } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { RiskBadge } from "@/components/shared/RiskBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { RiskAssessment } from "@/types/api";

export function RiskResultView({
  risk,
  animalId,
}: {
  risk: RiskAssessment;
  animalId: string;
}) {
  const { t } = useTranslation();

  const steps: string[] = [
    t("riskResult.steps.recheck"),
    t("riskResult.steps.keepRecords"),
    t("riskResult.steps.biosecurity"),
  ];
  if (risk.risk_band === "medium") steps.push(t("riskResult.steps.contactVetIfConcerned"));
  if (risk.risk_band === "high") steps.push(t("riskResult.steps.urgentVet"));

  const descriptionKey =
    risk.risk_band === "high"
      ? "riskResult.highDescription"
      : risk.risk_band === "medium"
        ? "riskResult.mediumDescription"
        : "riskResult.lowDescription";

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-4">
      <Card>
        <CardHeader className="items-center gap-3 text-center">
          <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            {t("riskResult.title")}
          </p>
          <RiskBadge band={risk.risk_band} className="px-4 py-2 text-base" />
          <p className="text-base">{t(descriptionKey)}</p>
        </CardHeader>

        {risk.risk_band === "high" && (
          <CardContent>
            <div className="rounded-xl border-2 border-[hsl(var(--risk-high))] bg-[hsl(var(--risk-high))]/10 p-4 text-center">
              <p className="font-semibold text-[hsl(var(--risk-high))]">{risk.clinical_disclaimer}</p>
            </div>
          </CardContent>
        )}
      </Card>

      {risk.top_factors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t("riskResult.whyThisResult")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-2">
              {risk.top_factors.slice(0, 4).map((factor) => (
                <li key={factor.rule} className="flex items-start gap-2 text-sm">
                  <span
                    className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-current"
                    aria-hidden="true"
                  />
                  {factor.reason}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("riskResult.safeNextSteps")}</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="flex flex-col gap-2">
            {steps.map((step) => (
              <li key={step} className="flex items-start gap-2 text-sm">
                <span
                  className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-current"
                  aria-hidden="true"
                />
                {step}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-2 sm:flex-row">
        {(risk.risk_band === "medium" || risk.risk_band === "high") && (
          <Button variant="destructive" size="lg" className="flex-1" asChild>
            <a href="tel:+911800000000">
              <Phone className="h-5 w-5" />
              {t("riskResult.contactVet")}
            </a>
          </Button>
        )}
        <Button variant="outline" size="lg" className="flex-1" asChild>
          <Link to={`/farmer/animals/${animalId}`}>{t("riskResult.backToDashboard")}</Link>
        </Button>
      </div>
    </div>
  );
}
