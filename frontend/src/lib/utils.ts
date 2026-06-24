import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRating(rating: number | null | undefined): string {
  if (rating == null) return "—";
  return rating.toFixed(1);
}

export function formatCost(cost: number | null | undefined): string {
  if (cost == null) return "Price not available";
  return `₹${cost.toLocaleString("en-IN")} for two`;
}
