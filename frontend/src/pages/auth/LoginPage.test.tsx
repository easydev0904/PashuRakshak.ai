import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import "@/i18n";
import { LoginPage } from "@/pages/auth/LoginPage";
import { AuthProvider } from "@/store/AuthContext";

vi.mock("@/services/authService", () => ({
  authService: {
    login: vi.fn().mockRejectedValue(new Error("network")),
    me: vi.fn().mockRejectedValue(new Error("no session")),
  },
}));

function renderLoginPage() {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("shows validation errors when submitted empty", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(screen.getByText(/please enter your email or phone number/i)).toBeInTheDocument();
      expect(screen.getByText(/please enter your password/i)).toBeInTheDocument();
    });
  });

  it("fills in demo credentials when a demo account is clicked", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    await user.click(screen.getByText("farmer.demo@pashurakshak.ai"));

    expect(screen.getByLabelText(/email or phone number/i)).toHaveValue(
      "farmer.demo@pashurakshak.ai",
    );
    expect(screen.getByLabelText(/password/i)).toHaveValue("Demo@1234");
  });
});
