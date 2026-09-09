import { Plus } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { AnimalCard } from "@/components/shared/AnimalCard";
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { useAnimals } from "@/hooks/useAnimals";
import { useFarms } from "@/hooks/useFarms";

export function AnimalsListPage() {
  const { t } = useTranslation();
  const farmsQuery = useFarms();
  const primaryFarm = farmsQuery.data?.[0];
  const animalsQuery = useAnimals(primaryFarm?.id);

  if (farmsQuery.isLoading || animalsQuery.isLoading) return <LoadingState />;
  if (animalsQuery.isError) return <ErrorState onRetry={() => animalsQuery.refetch()} />;

  const animals = animalsQuery.data ?? [];

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("nav.animals")}</h1>
        <Button size="sm" asChild>
          <Link to="/farmer/animals/new">
            <Plus className="h-4 w-4" />
            {t("farmerDashboard.registerAnimal")}
          </Link>
        </Button>
      </div>

      {animals.length === 0 ? (
        <EmptyState
          title={t("farmerDashboard.noAnimalsYet")}
          action={
            <Button asChild>
              <Link to="/farmer/animals/new">{t("farmerDashboard.registerAnimal")}</Link>
            </Button>
          }
        />
      ) : (
        <div className="flex flex-col gap-3">
          {animals.map((animal) => (
            <AnimalCard key={animal.id} animal={animal} />
          ))}
        </div>
      )}
    </div>
  );
}
