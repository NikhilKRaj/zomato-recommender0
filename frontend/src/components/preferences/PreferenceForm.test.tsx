import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PreferenceForm } from "@/components/preferences/PreferenceForm";

function renderForm(onSubmit = vi.fn()) {
  const queryClient = new QueryClient();
  return {
    onSubmit,
    ...render(
      <QueryClientProvider client={queryClient}>
        <PreferenceForm
          locations={["Koramangala", "Indiranagar"]}
          cuisines={["Italian", "Chinese"]}
          onSubmit={onSubmit}
        />
      </QueryClientProvider>,
    ),
  };
}

describe("PreferenceForm", () => {
  it("renders location as a dropdown", () => {
    renderForm();
    const locationSelect = screen.getByLabelText(/location/i);
    expect(locationSelect.tagName).toBe("SELECT");
    expect(screen.getByRole("option", { name: "Koramangala" })).toBeInTheDocument();
  });

  it("requires location and cuisine before submit", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderForm(onSubmit);

    await user.click(screen.getByRole("button", { name: /Get AI Recommendations/i }));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText("Please select a location")).toBeInTheDocument();
  });
});
