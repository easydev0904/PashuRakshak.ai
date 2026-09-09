import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RiskBadge } from "@/components/shared/RiskBadge";
import "@/i18n";

describe("RiskBadge", () => {
  it("renders the localized label for each risk band", () => {
    render(<RiskBadge band="low" />);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });

  it("renders HIGH band", () => {
    render(<RiskBadge band="high" />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("renders MEDIUM band", () => {
    render(<RiskBadge band="medium" />);
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });
});
