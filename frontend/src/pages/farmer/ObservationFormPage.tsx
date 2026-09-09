import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { OptionPicker } from "@/components/shared/OptionPicker";
import { RiskResultView } from "@/components/shared/RiskResultView";
import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAnimal, useSubmitObservation } from "@/hooks/useAnimals";
import {
  MAX_PLAUSIBLE_MILK_YIELD_CHANGE_PCT,
  MAX_PLAUSIBLE_TEMPERATURE_C,
  MIN_PLAUSIBLE_MILK_YIELD_CHANGE_PCT,
  MIN_PLAUSIBLE_TEMPERATURE_C,
} from "@/utils/observationLimits";
import type { RiskAssessment } from "@/types/api";

const schema = z.object({
  appetite: z.enum(["normal", "reduced", "none"]),
  activity: z.enum(["normal", "reduced", "lethargic"]),
  water_intake: z.enum(["normal", "reduced", "increased"]),
  respiratory_sign: z.enum(["none", "mild", "coughing", "labored"]),
  dung_sign: z.enum(["normal", "loose", "diarrhea", "bloody"]),
  temperature_c: z
    .string()
    .optional()
    .refine((v) => !v || (!isNaN(Number(v)) && Number(v) >= MIN_PLAUSIBLE_TEMPERATURE_C && Number(v) <= MAX_PLAUSIBLE_TEMPERATURE_C), {
      message: "Temperature must be between 30C and 45C",
    }),
  milk_yield_change_pct: z
    .string()
    .optional()
    .refine(
      (v) =>
        !v ||
        (!isNaN(Number(v)) &&
          Number(v) >= MIN_PLAUSIBLE_MILK_YIELD_CHANGE_PCT &&
          Number(v) <= MAX_PLAUSIBLE_MILK_YIELD_CHANGE_PCT),
      { message: "Milk yield change must be between -100% and 200%" },
    ),
  notes: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

const STEPS = ["appetite", "activity", "water_intake", "respiratory_sign", "dung_sign", "numbers"] as const;

export function ObservationFormPage() {
  const { t } = useTranslation();
  const { animalId } = useParams<{ animalId: string }>();
  const animalQuery = useAnimal(animalId);
  const submitObservation = useSubmitObservation(animalId ?? "");
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RiskAssessment | null>(null);

  const {
    control,
    register,
    handleSubmit,
    trigger,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      appetite: "normal",
      activity: "normal",
      water_intake: "normal",
      respiratory_sign: "none",
      dung_sign: "normal",
    },
  });

  if (animalQuery.isLoading) return <LoadingState />;
  if (animalQuery.isError || !animalQuery.data) return <ErrorState onRetry={() => animalQuery.refetch()} />;

  if (result && animalId) {
    return <RiskResultView risk={result} animalId={animalId} />;
  }

  const onSubmit = async (values: FormValues) => {
    setError(null);
    try {
      const response = await submitObservation.mutateAsync({
        appetite: values.appetite,
        activity: values.activity,
        water_intake: values.water_intake,
        respiratory_sign: values.respiratory_sign,
        dung_sign: values.dung_sign,
        temperature_c: values.temperature_c ? Number(values.temperature_c) : undefined,
        milk_yield_change_pct: values.milk_yield_change_pct
          ? Number(values.milk_yield_change_pct)
          : undefined,
        notes: values.notes || undefined,
      });
      setResult(response.risk_assessment);
    } catch (err) {
      setError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    }
  };

  const goNext = async () => {
    const fieldsToValidate: (keyof FormValues)[] =
      step < 5 ? [STEPS[step] as keyof FormValues] : [];
    const valid = fieldsToValidate.length === 0 || (await trigger(fieldsToValidate));
    if (valid) setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };
  const goPrevious = () => setStep((s) => Math.max(s - 1, 0));

  const levelOptions = (group: string, keys: string[]) =>
    keys.map((key) => ({ value: key, label: t(`observation.levels.${group}.${key}`) }));

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-4">
      <div>
        <h1 className="text-xl font-bold">{t("observation.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("observation.subtitle")}</p>
        <div className="mt-3 flex gap-1">
          {STEPS.map((s, idx) => (
            <div
              key={s}
              className={`h-1.5 flex-1 rounded-full ${idx <= step ? "bg-primary" : "bg-muted"}`}
            />
          ))}
        </div>
      </div>

      <Card>
        <CardContent className="p-5">
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">
            {step === 0 && (
              <div className="flex flex-col gap-3">
                <Label>{t("observation.appetite")}</Label>
                <Controller
                  control={control}
                  name="appetite"
                  render={({ field }) => (
                    <OptionPicker
                      name="appetite"
                      value={field.value}
                      onChange={field.onChange}
                      options={levelOptions("appetite", ["normal", "reduced", "none"])}
                    />
                  )}
                />
              </div>
            )}

            {step === 1 && (
              <div className="flex flex-col gap-3">
                <Label>{t("observation.activity")}</Label>
                <Controller
                  control={control}
                  name="activity"
                  render={({ field }) => (
                    <OptionPicker
                      name="activity"
                      value={field.value}
                      onChange={field.onChange}
                      options={levelOptions("activity", ["normal", "reduced", "lethargic"])}
                    />
                  )}
                />
              </div>
            )}

            {step === 2 && (
              <div className="flex flex-col gap-3">
                <Label>{t("observation.waterIntake")}</Label>
                <Controller
                  control={control}
                  name="water_intake"
                  render={({ field }) => (
                    <OptionPicker
                      name="water_intake"
                      value={field.value}
                      onChange={field.onChange}
                      options={levelOptions("water", ["normal", "reduced", "increased"])}
                    />
                  )}
                />
              </div>
            )}

            {step === 3 && (
              <div className="flex flex-col gap-3">
                <Label>{t("observation.respiratorySign")}</Label>
                <Controller
                  control={control}
                  name="respiratory_sign"
                  render={({ field }) => (
                    <OptionPicker
                      name="respiratory_sign"
                      value={field.value}
                      onChange={field.onChange}
                      options={levelOptions("respiratory", ["none", "mild", "coughing", "labored"])}
                    />
                  )}
                />
              </div>
            )}

            {step === 4 && (
              <div className="flex flex-col gap-3">
                <Label>{t("observation.dungSign")}</Label>
                <Controller
                  control={control}
                  name="dung_sign"
                  render={({ field }) => (
                    <OptionPicker
                      name="dung_sign"
                      value={field.value}
                      onChange={field.onChange}
                      options={levelOptions("dung", ["normal", "loose", "diarrhea", "bloody"])}
                    />
                  )}
                />
              </div>
            )}

            {step === 5 && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="temperature_c">
                    {t("observation.temperature")} ({t("common.optional")})
                  </Label>
                  <Input
                    id="temperature_c"
                    type="number"
                    step="0.1"
                    inputMode="decimal"
                    {...register("temperature_c")}
                  />
                  {errors.temperature_c && (
                    <p className="text-sm text-destructive">{errors.temperature_c.message}</p>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="milk_yield_change_pct">
                    {t("observation.milkYieldChange")} ({t("common.optional")})
                  </Label>
                  <Input
                    id="milk_yield_change_pct"
                    type="number"
                    step="1"
                    inputMode="numeric"
                    {...register("milk_yield_change_pct")}
                  />
                  {errors.milk_yield_change_pct && (
                    <p className="text-sm text-destructive">
                      {errors.milk_yield_change_pct.message}
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="notes">
                    {t("observation.notes")} ({t("common.optional")})
                  </Label>
                  <Textarea id="notes" {...register("notes")} />
                </div>
              </div>
            )}

            {error && (
              <p role="alert" className="text-sm text-destructive">
                {error}
              </p>
            )}

            <div className="flex gap-3">
              {step > 0 && (
                <Button type="button" variant="outline" className="flex-1" onClick={goPrevious}>
                  {t("common.previous")}
                </Button>
              )}
              {step < STEPS.length - 1 ? (
                <Button type="button" className="flex-1" onClick={goNext}>
                  {t("common.next")}
                </Button>
              ) : (
                <Button type="submit" className="flex-1" disabled={isSubmitting}>
                  {isSubmitting ? t("common.loading") : t("common.submit")}
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
