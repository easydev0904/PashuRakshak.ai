import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { useCreateUser, useUpdateUser, useUsers } from "@/hooks/useUsers";
import { stripEmptyStrings } from "@/utils/forms";

const createUserSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().optional(),
  phone: z.string().optional(),
  role: z.enum(["farmer", "veterinarian", "admin"]),
  password: z.string().min(8, "Password must be at least 8 characters"),
});
type CreateUserValues = z.infer<typeof createUserSchema>;

function CreateUserForm({ onDone }: { onDone: () => void }) {
  const createUser = useCreateUser();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateUserValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { role: "farmer" },
  });

  const onSubmit = async (values: CreateUserValues) => {
    setError(null);
    try {
      await createUser.mutateAsync(stripEmptyStrings(values) as CreateUserValues);
      onDone();
    } catch (err) {
      setError(friendlyErrorMessage(err, "Something went wrong. Please try again."));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3" noValidate>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-2">
          <Label htmlFor="name">Name</Label>
          <Input id="name" {...register("name")} />
          {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="role">Role</Label>
          <Select id="role" {...register("role")}>
            <option value="farmer">Farmer</option>
            <option value="veterinarian">Veterinarian</option>
            <option value="admin">Admin</option>
          </Select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" {...register("email")} />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="phone">Phone</Label>
          <Input id="phone" {...register("phone")} />
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="password">Temporary password</Label>
        <Input id="password" type="text" {...register("password")} />
        {errors.password && (
          <p className="text-sm text-destructive">{errors.password.message}</p>
        )}
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button type="submit" disabled={isSubmitting} className="self-start">
        Create user
      </Button>
    </form>
  );
}

export function AdminUsersPage() {
  const [showCreate, setShowCreate] = useState(false);
  const usersQuery = useUsers();
  const updateUser = useUpdateUser();

  if (usersQuery.isLoading) return <LoadingState />;
  if (usersQuery.isError) return <ErrorState onRetry={() => usersQuery.refetch()} />;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        <Button size="sm" onClick={() => setShowCreate((v) => !v)}>
          <UserPlus className="h-4 w-4" />
          Add user
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">New user</CardTitle>
          </CardHeader>
          <CardContent>
            <CreateUserForm onDone={() => setShowCreate(false)} />
          </CardContent>
        </Card>
      )}

      <div className="flex flex-col gap-2">
        {(usersQuery.data ?? []).map((user) => (
          <Card key={user.id}>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex-1">
                <p className="font-medium">{user.name}</p>
                <p className="text-sm text-muted-foreground">{user.email ?? user.phone}</p>
              </div>
              <Badge variant="outline" className="capitalize">
                {user.role}
              </Badge>
              <Badge variant={user.is_active ? "low" : "muted"}>
                {user.is_active ? "Active" : "Inactive"}
              </Badge>
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  updateUser.mutate({ userId: user.id, payload: { is_active: !user.is_active } })
                }
              >
                {user.is_active ? "Deactivate" : "Activate"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
