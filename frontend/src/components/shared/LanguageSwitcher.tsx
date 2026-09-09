import { Languages } from "lucide-react";
import { useTranslation } from "react-i18next";

import { cn } from "@/lib/utils";

const LANGUAGES: { code: "en" | "hi"; label: string }[] = [
  { code: "en", label: "EN" },
  { code: "hi", label: "हिं" },
];

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  return (
    <div className="flex items-center gap-1 rounded-full border border-border bg-muted/50 p-1">
      <Languages className="ml-1 h-4 w-4 text-muted-foreground" aria-hidden="true" />
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => i18n.changeLanguage(lang.code)}
          className={cn(
            "rounded-full px-2.5 py-1 text-xs font-semibold transition-colors",
            i18n.language === lang.code
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-muted",
          )}
          aria-pressed={i18n.language === lang.code}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
