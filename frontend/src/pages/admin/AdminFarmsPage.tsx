import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateFarm, useFarms } from "@/hooks/useFarms";
import { stripEmptyStrings } from "@/utils/forms";

const farmSchema = z.object({
  name: z.string().min(1, "Farm name is required"),
  village: z.string().optional(),
  district: z.string().optional(),
  state: z.string().optional(),
});
type FarmFormValues = z.infer<typeof farmSchema>;

function CreateFarmForm({ onDone }: { onDone: () => void }) {
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
      await createFarm.mutateAsync(stripEmptyStrings(values) as FarmFormValues);
      onDone();
    } catch (err) {
      setError(friendlyErrorMessage(err, "Something went wrong. Please try again."));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3" noValidate>
      <div className="flex flex-col gap-2">
        <Label htmlFor="name">Farm name</Label>
        <Input id="name" {...register("name")} />
        {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="flex flex-col gap-2">
          <Label htmlFor="village">Village</Label>
          <Input id="village" {...register("village")} />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="district">District</Label>
          <Input id="district" {...register("district")} />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="state">State</Label>
          <Input id="state" {...register("state")} />
        </div>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button type="submit" disabled={isSubmitting} className="self-start">
        Create farm
      </Button>
    </form>
  );
}

export function AdminFarmsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const farmsQuery = useFarms();

  if (farmsQuery.isLoading) return <LoadingState />;
  if (farmsQuery.isError) return <ErrorState onRetry={() => farmsQuery.refetch()} />;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Farms</h1>
        <Button size="sm" onClick={() => setShowCreate((v) => !v)}>
          <Plus className="h-4 w-4" />
          Add farm
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">New farm</CardTitle>
          </CardHeader>
          <CardContent>
            <CreateFarmForm onDone={() => setShowCreate(false)} />
          </CardContent>
        </Card>
      )}

      <div className="flex flex-col gap-2">
        {(farmsQuery.data ?? []).map((farm) => (
          <Card key={farm.id}>
            <CardContent className="p-4">
              <p className="font-medium">{farm.name}</p>
              <p className="text-sm text-muted-foreground">
                {[farm.village, farm.district, farm.state].filter(Boolean).join(", ") || "—"}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
