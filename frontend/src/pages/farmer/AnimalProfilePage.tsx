import { zodResolver } from "@hookform/resolvers/zod";
import { Beef, Plus, Syringe } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { AnimalTimeline } from "@/components/shared/AnimalTimeline";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAnimal, useObservations } from "@/hooks/useAnimals";
import { useAddVaccination, useVaccinations } from "@/hooks/useVaccinations";
import { useAuth } from "@/store/AuthContext";
import { stripEmptyStrings } from "@/utils/forms";

const vaccinationSchema = z.object({
  vaccine_name: z.string().min(1, "Vaccine name is required"),
  due_date: z.string().optional(),
  dose_date: z.string().optional(),
});
type VaccinationFormValues = z.infer<typeof vaccinationSchema>;

function AddVaccinationForm({ animalId, onDone }: { animalId: string; onDone: () => void }) {
  const { t } = useTranslation();
  const addVaccination = useAddVaccination(animalId);
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<VaccinationFormValues>({ resolver: zodResolver(vaccinationSchema) });

  const onSubmit = async (values: VaccinationFormValues) => {
    setError(null);
    try {
      await addVaccination.mutateAsync({
        ...stripEmptyStrings(values),
        vaccine_name: values.vaccine_name,
      });
      onDone();
    } catch (err) {
      setError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3" noValidate>
      <div className="flex flex-col gap-2">
        <Label htmlFor="vaccine_name">Vaccine name</Label>
        <Input id="vaccine_name" {...register("vaccine_name")} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-2">
          <Label htmlFor="dose_date">Given on ({t("common.optional")})</Label>
          <Input id="dose_date" type="date" {...register("dose_date")} />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="due_date">Next due ({t("common.optional")})</Label>
          <Input id="due_date" type="date" {...register("due_date")} />
        </div>
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting}>
        {t("common.save")}
      </Button>
    </form>
  );
}

export function AnimalProfilePage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { animalId } = useParams<{ animalId: string }>();
  const animalQuery = useAnimal(animalId);
  const observationsQuery = useObservations(animalId);
  const vaccinationsQuery = useVaccinations(animalId);
  const [showVaccinationForm, setShowVaccinationForm] = useState(false);

  if (animalQuery.isLoading) return <LoadingState />;
  if (animalQuery.isError || !animalQuery.data) {
    return <ErrorState onRetry={() => animalQuery.refetch()} />;
  }

  const animal = animalQuery.data;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <Card>
        <CardContent className="flex items-center gap-4 p-6">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Beef className="h-8 w-8" aria-hidden="true" />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold">{animal.tag_id}</h1>
            <p className="text-sm text-muted-foreground">
              {t(`animal.${animal.species}`)}
              {animal.breed ? ` · ${animal.breed}` : ""}
            </p>
          </div>
          {animal.last_risk_band && <RiskBadge band={animal.last_risk_band} />}
        </CardContent>
      </Card>

      {user?.role === "farmer" && (
        <Button size="lg" asChild>
          <Link to={`/farmer/animals/${animal.id}/observe`}>
            <Plus className="h-5 w-5" />
            {t("farmerDashboard.addObservation")}
          </Link>
        </Button>
      )}

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-base">{t("animal.vaccinations")}</CardTitle>
          {user?.role === "farmer" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowVaccinationForm((v) => !v)}
            >
              <Syringe className="h-4 w-4" />
              {t("animal.addVaccination")}
            </Button>
          )}
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {showVaccinationForm && animalId && (
            <AddVaccinationForm
              animalId={animalId}
              onDone={() => setShowVaccinationForm(false)}
            />
          )}
          {vaccinationsQuery.data && vaccinationsQuery.data.length > 0 ? (
            <ul className="flex flex-col gap-2 text-sm">
              {vaccinationsQuery.data.map((v) => (
                <li key={v.id} className="flex justify-between rounded-lg border border-border px-3 py-2">
                  <span>{v.vaccine_name}</span>
                  <span className="text-muted-foreground">
                    {v.due_date ? `Due ${v.due_date}` : v.dose_date ? `Given ${v.dose_date}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            !showVaccinationForm && (
              <p className="text-sm text-muted-foreground">{t("animal.noVaccinations")}</p>
            )
          )}
        </CardContent>
      </Card>

      <div>
        <h2 className="mb-3 text-lg font-semibold">{t("animal.profileTimeline")}</h2>
        {observationsQuery.isLoading ? (
          <LoadingState />
        ) : (
          <AnimalTimeline
            observations={observationsQuery.data ?? []}
            vaccinations={vaccinationsQuery.data ?? []}
          />
        )}
      </div>
    </div>
  );
}
