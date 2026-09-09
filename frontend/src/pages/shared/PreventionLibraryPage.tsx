import { Sprout } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { EmptyState, ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useEducationContent } from "@/hooks/useEducation";
import type { EducationCategory, Language } from "@/types/api";

const CATEGORIES: EducationCategory[] = [
  "vaccination",
  "hygiene",
  "quarantine",
  "nutrition",
  "biosecurity",
  "general_observation",
];

export function PreventionLibraryPage() {
  const { t, i18n } = useTranslation();
  const [category, setCategory] = useState<EducationCategory | undefined>(undefined);

  const contentQuery = useEducationContent({
    language: i18n.language as Language,
    category,
  });

  if (contentQuery.isLoading) return <LoadingState />;
  if (contentQuery.isError) return <ErrorState onRetry={() => contentQuery.refetch()} />;

  const content = contentQuery.data ?? [];

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <h1 className="text-2xl font-bold">{t("prevention.title")}</h1>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setCategory(undefined)}
          className={cn(
            "rounded-full px-3 py-1.5 text-sm font-medium",
            category === undefined
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-muted/70",
          )}
        >
          All
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={cn(
              "rounded-full px-3 py-1.5 text-sm font-medium",
              category === cat
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/70",
            )}
          >
            {t(`prevention.categories.${cat}`)}
          </button>
        ))}
      </div>

      {content.length === 0 ? (
        <EmptyState
          title="No prevention content yet"
          description="Check back soon, or switch categories."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {content.map((item) => (
            <Card key={item.id}>
              <CardHeader className="flex-row items-center gap-2">
                <Sprout className="h-4 w-4 text-primary" aria-hidden="true" />
                <CardTitle className="text-base">{item.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {t(`prevention.categories.${item.category}`)}
                </p>
                <p className="mt-2 whitespace-pre-wrap text-sm">{item.body}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
