import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { RiskResultView } from "@/components/shared/RiskResultView";
import "@/i18n";
import type { RiskAssessment } from "@/types/api";

const baseRisk: RiskAssessment = {
  id: "1",
  observation_id: "obs-1",
  model_version: "prototype-v1",
  risk_score: 0.9,
  risk_band: "high",
  top_factors: [{ rule: "appetite_loss", reason: "Animal is refusing food", severity: "high" }],
  human_review_required: true,
  clinical_disclaimer: "AI screening alert - veterinarian assessment required.",
  created_at: new Date().toISOString(),
};

function renderWithRouter(risk: RiskAssessment) {
  return render(
    <MemoryRouter>
      <RiskResultView risk={risk} animalId="animal-1" />
    </MemoryRouter>,
  );
}

describe("RiskResultView", () => {
  it("shows the mandatory disclaimer for HIGH risk", () => {
    renderWithRouter(baseRisk);
    expect(
      screen.getByText("AI screening alert - veterinarian assessment required."),
    ).toBeInTheDocument();
  });

  it("shows contributing factors", () => {
    renderWithRouter(baseRisk);
    expect(screen.getByText("Animal is refusing food")).toBeInTheDocument();
  });

  it("shows the contact-vet action for HIGH risk", () => {
    renderWithRouter(baseRisk);
    expect(screen.getByText("Contact veterinarian")).toBeInTheDocument();
  });

  it("does not show the disclaimer box for LOW risk", () => {
    renderWithRouter({ ...baseRisk, risk_band: "low", human_review_required: false });
    expect(
      screen.queryByText("AI screening alert - veterinarian assessment required."),
    ).not.toBeInTheDocument();
  });

  it("never renders a diagnosis or treatment claim", () => {
    renderWithRouter(baseRisk);
    const bodyText = document.body.textContent ?? "";
    expect(bodyText.toLowerCase()).not.toContain("diagnosis");
    expect(bodyText.toLowerCase()).not.toContain("treatment:");
    expect(bodyText.toLowerCase()).not.toContain("prescription");
  });
});
