import { useMutation } from "@tanstack/react-query";

import { api } from "@/api/client";
import type { RecommendationResponse, UserPreferences } from "@/api/types";

export function useRecommendations() {
  return useMutation<RecommendationResponse, Error, UserPreferences>({
    mutationFn: (preferences) => api.recommend(preferences),
  });
}
