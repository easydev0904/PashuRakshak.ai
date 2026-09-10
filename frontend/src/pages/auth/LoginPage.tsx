import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { LanguageSwitcher } from "@/components/shared/LanguageSwitcher";
import { homeRouteForRole } from "@/components/shared/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/store/AuthContext";

const schema = z.object({
  identifier: z.string().min(1, "Please enter your email or phone number"),
  password: z.string().min(1, "Please enter your password"),
});
type FormValues = z.infer<typeof schema>;

const DEMO_ACCOUNTS = [
  { role: "Farmer", email: "farmer.demo@pashurakshak.ai" },
  { role: "Veterinarian", email: "vet.demo@pashurakshak.ai" },
  { role: "Admin", email: "admin.demo@pashurakshak.ai" },
];
const DEMO_PASSWORD = "Demo@1234";

export function LoginPage() {
  const { t } = useTranslation();
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  if (user) {
    const target = (location.state as { from?: string } | null)?.from ?? homeRouteForRole(user.role);
    return <Navigate to={target} replace />;
  }

  const onSubmit = async (values: FormValues) => {
    setServerError(null);
    const isEmail = values.identifier.includes("@");
    try {
      const loggedInUser = await login({
        email: isEmail ? values.identifier : undefined,
        phone: isEmail ? undefined : values.identifier,
        password: values.password,
      });
      navigate(homeRouteForRole(loggedInUser.role), { replace: true });
    } catch (error) {
      setServerError(friendlyErrorMessage(error, t("auth.loginError")));
    }
  };

  const fillDemo = (email: string) => {
    setValue("identifier", email);
    setValue("password", DEMO_PASSWORD);
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-4 py-10">
      <div className="flex flex-col items-center gap-1 text-center">
        <h1 className="text-2xl font-bold text-primary">{t("app.name")}</h1>
        <p className="text-sm text-muted-foreground">{t("app.tagline")}</p>
      </div>

      <LanguageSwitcher />

      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{t("auth.login")}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-2">
              <Label htmlFor="identifier">{t("auth.emailOrPhone")}</Label>
              <Input
                id="identifier"
                autoComplete="username"
                {...register("identifier")}
                aria-invalid={!!errors.identifier}
              />
              {errors.identifier && (
                <p className="text-sm text-destructive">{errors.identifier.message}</p>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="password">{t("auth.password")}</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register("password")}
                aria-invalid={!!errors.password}
              />
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password.message}</p>
              )}
            </div>

            {serverError && (
              <p role="alert" className="text-sm text-destructive">
                {serverError}
              </p>
            )}

            <Button type="submit" className="mt-2 w-full" disabled={isSubmitting}>
              {isSubmitting ? t("common.loading") : t("auth.loginButton")}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="w-full max-w-sm bg-muted/40">
        <CardHeader>
          <CardTitle className="text-sm">{t("auth.demoAccounts")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {DEMO_ACCOUNTS.map((account) => (
            <button
              key={account.email}
              type="button"
              onClick={() => fillDemo(account.email)}
              className="flex items-center justify-between rounded-lg border border-border bg-card px-3 py-2 text-left text-sm hover:bg-muted"
            >
              <span className="font-medium">{account.role}</span>
              <span className="text-muted-foreground">{account.email}</span>
            </button>
          ))}
          <p className="text-xs text-muted-foreground">Password for all demo accounts: {DEMO_PASSWORD}</p>
        </CardContent>
      </Card>
    </div>
  );
}
