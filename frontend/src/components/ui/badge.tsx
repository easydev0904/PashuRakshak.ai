import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold whitespace-nowrap",
  {
    variants: {
      variant: {
        default: "bg-primary/10 text-primary",
        secondary: "bg-secondary/20 text-secondary-foreground",
        outline: "border border-border text-foreground",
        low: "bg-[hsl(var(--risk-low))]/15 text-[hsl(var(--risk-low))]",
        medium: "bg-[hsl(var(--risk-medium))]/15 text-[hsl(var(--risk-medium))]",
        high: "bg-[hsl(var(--risk-high))]/15 text-[hsl(var(--risk-high))]",
        muted: "bg-muted text-muted-foreground",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
