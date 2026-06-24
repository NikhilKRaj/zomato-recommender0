import type {
  MetadataBudgetBands,
  MetadataCuisines,
  MetadataLocations,
  RecommendationResponse,
  UserPreferences,
} from "./types";

const API_BASE = (
  import.meta.env.VITE_API_URL ??
  import.meta.env.RAILWAY_API_URL ??
  "/api"
).replace(/\/$/, "");

export class ApiClientError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: unknown,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new ApiClientError(
      "Could not reach the backend API. Confirm RAILWAY_API_URL is set in Vercel and redeploy.",
      response.status,
    );
  }

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      detail = undefined;
    }
    const message =
      response.status === 404
        ? "No restaurants match your filters. Try broadening your search."
        : response.status === 400
          ? "Please check your preferences and try again."
          : response.status === 502
            ? "The backend API is not configured. Set RAILWAY_API_URL in Vercel."
            : response.status === 503
              ? "The recommendation service is temporarily unavailable."
              : "Something went wrong. Please try again.";
    throw new ApiClientError(message, response.status, detail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getLocations: () => request<MetadataLocations>("/metadata/locations"),
  getCuisines: () => request<MetadataCuisines>("/metadata/cuisines"),
  getBudgetBands: () => request<MetadataBudgetBands>("/metadata/budget-bands"),
  recommend: (preferences: UserPreferences) =>
    request<RecommendationResponse>("/recommend", {
      method: "POST",
      body: JSON.stringify(preferences),
    }),
};
