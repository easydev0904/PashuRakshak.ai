import { cn } from "@/lib/utils";

export interface Option {
  value: string;
  label: string;
}

export function OptionPicker({
  options,
  value,
  onChange,
  name,
}: {
  options: Option[];
  value: string | undefined;
  onChange: (value: string) => void;
  name: string;
}) {
  return (
    <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={name}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          role="radio"
          aria-checked={value === option.value}
          onClick={() => onChange(option.value)}
          className={cn(
            "min-h-[48px] flex-1 rounded-xl border-2 px-4 py-2 text-sm font-medium transition-colors",
            "min-w-[100px] basis-[45%] sm:basis-auto",
            value === option.value
              ? "border-primary bg-primary text-primary-foreground"
              : "border-border bg-card text-foreground hover:border-primary/50",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
