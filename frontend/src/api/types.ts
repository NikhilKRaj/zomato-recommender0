export type BudgetBand = "low" | "medium" | "high";

export interface Restaurant {
  id: string;
  name: string;
  location: string;
  city: string;
  cuisines: string[];
  rating: number | null;
  votes: number;
  cost_for_two: number | null;
  budget_band: BudgetBand | null;
  rest_type: string;
  meal_type: string;
  online_order: boolean;
  book_table: boolean;
  dish_liked: string | null;
  address: string;
  url: string | null;
}

export interface UserPreferences {
  location: string;
  budget: BudgetBand;
  cuisine: string;
  min_rating: number;
  additional_preferences?: string | null;
  top_n: number;
}

export interface Recommendation {
  rank: number;
  restaurant: Restaurant;
  explanation: string;
}

export interface ResponseMeta {
  candidates_considered: number;
  source: "llm" | "fallback";
  model: string | null;
}

export interface RecommendationResponse {
  summary: string | null;
  recommendations: Recommendation[];
  meta: ResponseMeta;
}

export interface BudgetBandDefinition {
  label: string;
  min_cost?: number;
  max_cost?: number;
}

export interface MetadataLocations {
  locations: string[];
}

export interface MetadataCuisines {
  cuisines: string[];
}

export interface MetadataBudgetBands {
  budget_bands: Record<BudgetBand, BudgetBandDefinition>;
}

export interface ApiErrorDetail {
  detail: string | Array<{ msg: string; loc: string[] }>;
}
