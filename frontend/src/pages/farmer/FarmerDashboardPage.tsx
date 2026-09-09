import { Plus } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { AnimalCard } from "@/components/shared/AnimalCard";
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAnimals } from "@/hooks/useAnimals";
import { useFarms } from "@/hooks/useFarms";
import { useAuth } from "@/store/AuthContext";

export function FarmerDashboardPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const farmsQuery = useFarms();
  const primaryFarm = farmsQuery.data?.[0];
  const animalsQuery = useAnimals(primaryFarm?.id);

  if (farmsQuery.isLoading || animalsQuery.isLoading) return <LoadingState />;
  if (farmsQuery.isError) {
    return <ErrorState onRetry={() => farmsQuery.refetch()} />;
  }

  const animals = animalsQuery.data ?? [];
  const needingCheckin = animals.filter((a) => a.needs_checkin_today);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">
          {t("farmerDashboard.greeting", { name: user?.name.split(" ")[0] ?? "" })}
        </h1>
        {primaryFarm && <p className="text-muted-foreground">{primaryFarm.name}</p>}
      </div>

      {animals.length > 0 && (
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="flex flex-col items-start gap-4 p-6">
            <p className="text-lg font-semibold">
              {needingCheckin.length > 0
                ? t("farmerDashboard.checkinCount", { count: needingCheckin.length })
                : t("farmerDashboard.allCaughtUp")}
            </p>
            <Button size="lg" variant={needingCheckin.length > 0 ? "default" : "outline"} asChild>
              <Link to={`/farmer/animals/${(needingCheckin[0] ?? animals[0]).id}/observe`}>
                <Plus className="h-5 w-5" />
                {t("farmerDashboard.addObservation")}
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">{t("farmerDashboard.yourAnimals")}</h2>
          <Button variant="ghost" size="sm" asChild>
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
    </div>
  );
}
