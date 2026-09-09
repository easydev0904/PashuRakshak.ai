import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import "@/i18n";
import { PreventionLibraryPage } from "@/pages/shared/PreventionLibraryPage";
import type { EducationContent } from "@/types/api";

const { SAMPLE_CONTENT } = vi.hoisted(() => ({
  SAMPLE_CONTENT: [
    {
      id: "1",
      category: "hygiene",
      title: "Clean water troughs weekly",
      language: "en",
      body: "Empty and scrub water troughs regularly.",
      audience: "farmer",
      is_published: true,
    },
  ] satisfies EducationContent[],
}));

vi.mock("@/services/educationService", () => ({
  educationService: {
    list: vi.fn().mockResolvedValue(SAMPLE_CONTENT),
  },
}));

function renderPage() {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <PreventionLibraryPage />
    </QueryClientProvider>,
  );
}

describe("PreventionLibraryPage", () => {
  it("renders published content", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Clean water troughs weekly")).toBeInTheDocument();
    });
  });

  it("never claims an outbreak", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Clean water troughs weekly")).toBeInTheDocument();
    });
    expect(document.body.textContent?.toLowerCase()).not.toContain("outbreak");
  });
});
