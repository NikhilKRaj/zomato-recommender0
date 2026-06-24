import { useQuery } from "@tanstack/react-query";

import { api } from "@/api/client";

export function useMetadata() {
  const locations = useQuery({
    queryKey: ["metadata", "locations"],
    queryFn: () => api.getLocations(),
    staleTime: 5 * 60 * 1000,
  });

  const cuisines = useQuery({
    queryKey: ["metadata", "cuisines"],
    queryFn: () => api.getCuisines(),
    staleTime: 5 * 60 * 1000,
  });

  const budgetBands = useQuery({
    queryKey: ["metadata", "budget-bands"],
    queryFn: () => api.getBudgetBands(),
    staleTime: Infinity,
  });

  return {
    locations: locations.data?.locations ?? [],
    cuisines: cuisines.data?.cuisines ?? [],
    budgetBands: budgetBands.data?.budget_bands ?? null,
    isLoading: locations.isLoading || cuisines.isLoading || budgetBands.isLoading,
    isError: locations.isError || cuisines.isError || budgetBands.isError,
    error: locations.error ?? cuisines.error ?? budgetBands.error,
  };
}
