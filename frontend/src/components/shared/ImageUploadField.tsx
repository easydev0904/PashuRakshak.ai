import { ImagePlus, Loader2, X } from "lucide-react";
import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { friendlyErrorMessage, resolveMediaUrl } from "@/api/client";
import { Button } from "@/components/ui/button";
import { uploadService } from "@/services/uploadService";
import { ALLOWED_IMAGE_TYPES, MAX_UPLOAD_SIZE_MB } from "@/utils/uploadLimits";

export function ImageUploadField({
  value,
  onChange,
  label,
}: {
  value: string | undefined;
  onChange: (url: string | undefined) => void;
  label: string;
}) {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File | undefined) => {
    if (!file) return;
    setError(null);

    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setError("Please choose a JPEG, PNG, or WEBP image.");
      return;
    }
    if (file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024) {
      setError(`Images must be ${MAX_UPLOAD_SIZE_MB}MB or smaller.`);
      return;
    }

    setIsUploading(true);
    try {
      const url = await uploadService.uploadImage(file);
      onChange(url);
    } catch (err) {
      setError(friendlyErrorMessage(err, t("common.somethingWentWrong")));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">{label}</label>
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_IMAGE_TYPES.join(",")}
        className="hidden"
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />

      {value ? (
        <div className="relative w-fit">
          <img
            src={resolveMediaUrl(value)}
            alt=""
            className="h-32 w-32 rounded-xl border border-border object-cover"
          />
          <button
            type="button"
            onClick={() => onChange(undefined)}
            className="absolute -right-2 -top-2 rounded-full bg-destructive p-1 text-destructive-foreground"
            aria-label="Remove photo"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      ) : (
        <Button
          type="button"
          variant="outline"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
          className="w-fit"
        >
          {isUploading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <ImagePlus className="h-4 w-4" />
          )}
          {isUploading ? t("common.loading") : "Add photo"}
        </Button>
      )}

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
