import { CheckCircle2, ClipboardCheck, Stethoscope, UserCheck } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";

import { friendlyErrorMessage } from "@/api/client";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useAlert, useReviewAlert } from "@/hooks/useAlerts";
import { useCasesForAnimal, useUpdateCaseClinical } from "@/hooks/useCases";
import { useAuth } from "@/store/AuthContext";

const OBSERVATION_FIELDS: { key: string; label: string }[] = [
  { key: "appetite", label: "Appetite" },
  { key: "activity", label: "Activity" },
  { key: "water_intake", label: "Water intake" },
  { key: "respiratory_sign", label: "Respiratory sign" },
  { key: "dung_sign", label: "Dung sign" },
];

function CaseSection({ animalId, alertId }: { animalId: string; alertId: string }) {
  const { t } = useTranslation();
  const casesQuery = useCasesForAnimal(animalId);
  const relatedCase = casesQuery.data?.find((c) => c.alert_id === alertId);
  const updateCase = useUpdateCaseClinical(relatedCase?.id ?? "", animalId);
  const [confirmed, setConfirmed] = useState("");
  const [basis, setBasis] = useState("");
  const [error, setError] = useState<string | null>(null);

  if (!relatedCase) {
    return (
      <p className="text-sm text-muted-foreground">
        No case has been opened for this alert yet. Use "Request follow-up" to open one.
      </p>
    );
  }

  const onSaveClinical = async () => {
    setError(null);
    try {
      await updateCase.mutateAsync({
        confirmed_condition: confirmed || undefined,
        confirmation_basis: basis || undefined,
      });
      setConfirmed("");
      setBasis("");
    } catch (err) {
      setError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Badge variant="outline">{relatedCase.status}</Badge>
        {relatedCase.suspected_condition && (
          <span className="text-sm">Suspected: {relatedCase.suspected_condition}</span>
        )}
      </div>

      {relatedCase.confirmed_condition ? (
        <div className="rounded-xl border border-border bg-muted/40 p-3 text-sm">
          <p className="font-medium">{t("case.confirmedCondition")}</p>
          <p>{relatedCase.confirmed_condition}</p>
          {relatedCase.confirmation_basis && (
            <p className="mt-1 text-muted-foreground">{relatedCase.confirmation_basis}</p>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">{t("case.confirmedCondition")}</label>
          <Textarea
            value={confirmed}
            onChange={(e) => setConfirmed(e.target.value)}
            placeholder="Enter only after your own clinical assessment"
          />
          <label className="text-sm font-medium">{t("case.confirmationBasis")}</label>
          <Textarea value={basis} onChange={(e) => setBasis(e.target.value)} />
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button
            size="sm"
            className="self-start"
            onClick={onSaveClinical}
            disabled={!confirmed || updateCase.isPending}
          >
            <Stethoscope className="h-4 w-4" />
            {t("common.save")}
          </Button>
        </div>
      )}

      {relatedCase.updates && relatedCase.updates.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium">{t("case.clinicalNotes")}</p>
          {relatedCase.updates.map((update) => (
            <div key={update.id} className="rounded-lg border border-border p-2 text-sm">
              <p>{update.note}</p>
              <p className="text-xs text-muted-foreground">
                {new Date(update.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function AlertDetailPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { alertId } = useParams<{ alertId: string }>();
  const alertQuery = useAlert(alertId);
  const reviewAlert = useReviewAlert(alertId ?? "");
  const [note, setNote] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);

  if (alertQuery.isLoading) return <LoadingState />;
  if (alertQuery.isError || !alertQuery.data) {
    return <ErrorState onRetry={() => alertQuery.refetch()} />;
  }

  const alert = alertQuery.data;

  const runAction = async (action: "acknowledge" | "assign" | "request_follow_up" | "resolve") => {
    setActionError(null);
    try {
      await reviewAlert.mutateAsync({
        action,
        assigned_vet_id: action === "assign" ? user?.id : undefined,
        note: note || undefined,
      });
      setNote("");
    } catch (err) {
      setActionError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    }
  };

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">
            {alert.animal.tag_id} · {alert.farm_name}
          </h1>
          <p className="text-sm text-muted-foreground">{t(`animal.${alert.animal.species}`)}</p>
        </div>
        <Badge variant="outline">{alert.status}</Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("alertDetail.reportedObservation")}</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 text-sm">
          {OBSERVATION_FIELDS.map((field) => (
            <div key={field.key}>
              <p className="text-muted-foreground">{field.label}</p>
              <p className="font-medium capitalize">
                {(alert.observation as unknown as Record<string, string>)[field.key]}
              </p>
            </div>
          ))}
          {alert.observation.temperature_c != null && (
            <div>
              <p className="text-muted-foreground">Temperature</p>
              <p className="font-medium">{alert.observation.temperature_c} C</p>
            </div>
          )}
          {alert.observation.milk_yield_change_pct != null && (
            <div>
              <p className="text-muted-foreground">Milk yield change</p>
              <p className="font-medium">{alert.observation.milk_yield_change_pct}%</p>
            </div>
          )}
          {alert.observation.notes && (
            <div className="col-span-2">
              <p className="text-muted-foreground">Notes</p>
              <p className="font-medium">{alert.observation.notes}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-base">{t("alertDetail.aiScreening")}</CardTitle>
          <RiskBadge band={alert.risk_assessment.risk_band} />
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <p className="text-xs text-muted-foreground">
            Model version: {alert.risk_assessment.model_version}
          </p>
          <div>
            <p className="mb-1 text-sm font-medium">{t("alertDetail.contributingSignals")}</p>
            <ul className="list-inside list-disc text-sm text-muted-foreground">
              {alert.risk_assessment.top_factors.map((factor) => (
                <li key={factor.rule}>{factor.reason}</li>
              ))}
            </ul>
          </div>
          {alert.risk_assessment.human_review_required && (
            <div className="rounded-lg border border-[hsl(var(--risk-high))] bg-[hsl(var(--risk-high))]/10 p-3 text-sm font-medium text-[hsl(var(--risk-high))]">
              {alert.risk_assessment.clinical_disclaimer}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("alertDetail.veterinaryAssessment")}</CardTitle>
        </CardHeader>
        <CardContent>
          <CaseSection animalId={alert.animal.id} alertId={alert.id} />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex flex-col gap-3 p-5">
          <Textarea
            placeholder="Optional note for this action"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          {actionError && <p className="text-sm text-destructive">{actionError}</p>}
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              onClick={() => runAction("acknowledge")}
              disabled={reviewAlert.isPending}
            >
              <CheckCircle2 className="h-4 w-4" />
              {t("alertDetail.acknowledge")}
            </Button>
            <Button
              variant="outline"
              onClick={() => runAction("assign")}
              disabled={reviewAlert.isPending}
            >
              <UserCheck className="h-4 w-4" />
              {t("alertDetail.assign")}
            </Button>
            <Button
              variant="secondary"
              onClick={() => runAction("request_follow_up")}
              disabled={reviewAlert.isPending}
            >
              <ClipboardCheck className="h-4 w-4" />
              {t("alertDetail.requestFollowUp")}
            </Button>
            <Button
              variant="destructive"
              onClick={() => runAction("resolve")}
              disabled={reviewAlert.isPending}
            >
              {t("alertDetail.resolve")}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
