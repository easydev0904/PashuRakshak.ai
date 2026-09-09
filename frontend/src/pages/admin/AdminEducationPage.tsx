import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { z } from "zod";

import { friendlyErrorMessage } from "@/api/client";
import { ErrorState, LoadingState } from "@/components/shared/StateViews";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  useAllEducationContentForAdmin,
  useCreateEducationContent,
  useUpdateEducationContent,
} from "@/hooks/useEducation";

const CATEGORIES = [
  "vaccination",
  "hygiene",
  "quarantine",
  "nutrition",
  "biosecurity",
  "general_observation",
] as const;

const contentSchema = z.object({
  title: z.string().min(1, "Title is required"),
  category: z.enum(CATEGORIES),
  language: z.enum(["en", "hi"]),
  body: z.string().min(1, "Body is required"),
  audience: z.enum(["farmer", "veterinarian", "all"]),
});
type ContentFormValues = z.infer<typeof contentSchema>;

function CreateContentForm({ onDone }: { onDone: () => void }) {
  const createContent = useCreateEducationContent();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ContentFormValues>({
    resolver: zodResolver(contentSchema),
    defaultValues: { category: "vaccination", language: "en", audience: "all" },
  });

  const onSubmit = async (values: ContentFormValues) => {
    setError(null);
    try {
      await createContent.mutateAsync(values);
      onDone();
    } catch (err) {
      setError(friendlyErrorMessage(err, "Something went wrong. Please try again."));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3" noValidate>
      <div className="flex flex-col gap-2">
        <Label htmlFor="title">Title</Label>
        <Input id="title" {...register("title")} />
        {errors.title && <p className="text-sm text-destructive">{errors.title.message}</p>}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="flex flex-col gap-2">
          <Label htmlFor="category">Category</Label>
          <Select id="category" {...register("category")}>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat.replace("_", " ")}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="language">Language</Label>
          <Select id="language" {...register("language")}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="audience">Audience</Label>
          <Select id="audience" {...register("audience")}>
            <option value="all">All</option>
            <option value="farmer">Farmer</option>
            <option value="veterinarian">Veterinarian</option>
          </Select>
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="body">Body</Label>
        <Textarea id="body" rows={5} {...register("body")} />
        {errors.body && <p className="text-sm text-destructive">{errors.body.message}</p>}
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button type="submit" disabled={isSubmitting} className="self-start">
        Publish content
      </Button>
    </form>
  );
}

export function AdminEducationPage() {
  const { t } = useTranslation();
  const [showCreate, setShowCreate] = useState(false);
  const contentQuery = useAllEducationContentForAdmin();
  const updateContent = useUpdateEducationContent();

  if (contentQuery.isLoading) return <LoadingState />;
  if (contentQuery.isError) return <ErrorState onRetry={() => contentQuery.refetch()} />;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("admin.educationTitle")}</h1>
        <Button size="sm" onClick={() => setShowCreate((v) => !v)}>
          <Plus className="h-4 w-4" />
          {t("admin.createContent")}
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">New content</CardTitle>
          </CardHeader>
          <CardContent>
            <CreateContentForm onDone={() => setShowCreate(false)} />
          </CardContent>
        </Card>
      )}

      <div className="flex flex-col gap-2">
        {(contentQuery.data ?? []).map((content) => (
          <Card key={content.id}>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex-1">
                <p className="font-medium">{content.title}</p>
                <p className="text-sm text-muted-foreground">
                  {content.category.replace("_", " ")} · {content.language.toUpperCase()}
                </p>
              </div>
              <Badge variant={content.is_published ? "low" : "muted"}>
                {content.is_published ? t("admin.published") : t("admin.unpublished")}
              </Badge>
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  updateContent.mutate({
                    contentId: content.id,
                    payload: { is_published: !content.is_published },
                  })
                }
              >
                {content.is_published ? "Unpublish" : "Publish"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
