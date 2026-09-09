import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { LoadingState } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useCreateAnimal } from "@/hooks/useAnimals";
import { useCreateFarm, useFarms } from "@/hooks/useFarms";
import { stripEmptyStrings } from "@/utils/forms";

const farmSchema = z.object({
  name: z.string().min(1, "Farm name is required"),
  village: z.string().optional(),
});
type FarmFormValues = z.infer<typeof farmSchema>;

const animalSchema = z.object({
  tag_id: z.string().min(1, "Tag ID is required"),
  species: z.enum(["cattle", "buffalo"]),
  breed: z.string().optional(),
  sex: z.enum(["male", "female"]),
  dob: z.string().optional(),
  notes: z.string().optional(),
});
type AnimalFormValues = z.infer<typeof animalSchema>;

function CreateFarmForm() {
  const { t } = useTranslation();
  const createFarm = useCreateFarm();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FarmFormValues>({ resolver: zodResolver(farmSchema) });

  const onSubmit = async (values: FarmFormValues) => {
    setError(null);
    try {
      await createFarm.mutateAsync(values);
    } catch (err) {
      setError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    }
  };

  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <CardTitle>Let's set up your farm first</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
          <div className="flex flex-col gap-2">
            <Label htmlFor="farm-name">Farm name</Label>
            <Input id="farm-name" {...register("name")} aria-invalid={!!errors.name} />
            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="farm-village">Village ({t("common.optional")})</Label>
            <Input id="farm-village" {...register("village")} />
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
      </CardContent>
    </Card>
  );
}

export function AnimalRegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const farmsQuery = useFarms();
  const createAnimal = useCreateAnimal();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AnimalFormValues>({
    resolver: zodResolver(animalSchema),
    defaultValues: { species: "cattle", sex: "female" },
  });

  if (farmsQuery.isLoading) return <LoadingState />;

  const primaryFarm = farmsQuery.data?.[0];
  if (!primaryFarm) return <CreateFarmForm />;

  const onSubmit = async (values: AnimalFormValues) => {
    setError(null);
    try {
      const animal = await createAnimal.mutateAsync({
        ...stripEmptyStrings(values),
        tag_id: values.tag_id,
        species: values.species,
        sex: values.sex,
        farm_id: primaryFarm.id,
      });
      navigate(`/farmer/animals/${animal.id}`, { replace: true });
    } catch (err) {
      setError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    }
  };

  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <CardTitle>{t("animal.registerTitle")}</CardTitle>
        <p className="text-sm text-muted-foreground">{t("animal.registerSubtitle")}</p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
          <div className="flex flex-col gap-2">
            <Label htmlFor="tag_id">{t("animal.tagId")}</Label>
            <Input id="tag_id" {...register("tag_id")} aria-invalid={!!errors.tag_id} />
            {errors.tag_id && <p className="text-sm text-destructive">{errors.tag_id.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="species">{t("animal.species")}</Label>
              <Select id="species" {...register("species")}>
                <option value="cattle">{t("animal.cattle")}</option>
                <option value="buffalo">{t("animal.buffalo")}</option>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="sex">{t("animal.sex")}</Label>
              <Select id="sex" {...register("sex")}>
                <option value="female">{t("animal.female")}</option>
                <option value="male">{t("animal.male")}</option>
              </Select>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="breed">
              {t("animal.breed")} ({t("common.optional")})
            </Label>
            <Input id="breed" {...register("breed")} />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="dob">
              {t("animal.dob")} ({t("common.optional")})
            </Label>
            <Input id="dob" type="date" {...register("dob")} />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="notes">
              {t("animal.notes")} ({t("common.optional")})
            </Label>
            <Textarea id="notes" {...register("notes")} />
          </div>

          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}

          <Button type="submit" size="lg" disabled={isSubmitting}>
            {isSubmitting ? t("common.loading") : t("common.save")}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
