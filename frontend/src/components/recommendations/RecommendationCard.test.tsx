import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { Recommendation } from "@/api/types";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";

const mockRecommendation: Recommendation = {
  rank: 1,
  explanation: "Great Italian spot for families.",
  restaurant: {
    id: "1",
    name: "Truffles",
    location: "Koramangala",
    city: "Bangalore",
    cuisines: ["Italian", "American"],
    rating: 4.5,
    votes: 100,
    cost_for_two: 500,
    budget_band: "medium",
    rest_type: "Casual Dining",
    meal_type: "Cafes",
    online_order: true,
    book_table: true,
    dish_liked: null,
    address: "Koramangala, Bangalore",
    url: "https://www.zomato.com/truffles",
  },
};

describe("RecommendationCard", () => {
  it("renders restaurant name, rating, and explanation", () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);

    expect(screen.getByText("Truffles")).toBeInTheDocument();
    expect(screen.getByText("4.5")).toBeInTheDocument();
    expect(screen.getByText(/Great Italian spot for families/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /View on Zomato/i })).toBeInTheDocument();
  });

  it("does not render food images", () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
});
