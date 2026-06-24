import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { BudgetBand, UserPreferences } from "@/api/types";
import { Icon } from "@/components/ui/Icon";
import { cn } from "@/lib/utils";

import { BudgetSelector } from "./BudgetSelector";
import { CuisineSelect } from "./CuisineSelect";
import { LocationSelect } from "./LocationSelect";
import { RatingSlider } from "./RatingSlider";

const preferenceSchema = z.object({
  location: z.string().min(1, "Please select a location"),
  budget: z.enum(["low", "medium", "high"]),
  cuisine: z.string().min(1, "Please select a cuisine"),
  min_rating: z.number().min(0).max(5),
  additional_preferences: z
    .string()
    .max(500, "Must be at most 500 characters")
    .optional(),
  top_n: z.number().min(1).max(10),
});

type PreferenceFormValues = z.infer<typeof preferenceSchema>;

interface PreferenceFormProps {
  locations: string[];
  cuisines: string[];
  isLoading?: boolean;
  isSubmitting?: boolean;
  onSubmit: (preferences: UserPreferences) => void;
}

export function PreferenceForm({
  locations,
  cuisines,
  isLoading,
  isSubmitting,
  onSubmit,
}: PreferenceFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<PreferenceFormValues>({
    resolver: zodResolver(preferenceSchema),
    defaultValues: {
      location: "",
      budget: "medium",
      cuisine: "",
      min_rating: 0,
      additional_preferences: "",
      top_n: 5,
    },
  });

  const location = watch("location");
  const budget = watch("budget");
  const cuisine = watch("cuisine");
  const minRating = watch("min_rating");
  const topN = watch("top_n");
  const additionalPreferences = watch("additional_preferences") ?? "";

  const submitHandler = (values: PreferenceFormValues) => {
    onSubmit({
      location: values.location,
      budget: values.budget,
      cuisine: values.cuisine,
      min_rating: values.min_rating,
      additional_preferences: values.additional_preferences?.trim() || null,
      top_n: values.top_n,
    });
  };

  const disabled = isLoading || isSubmitting;

  return (
    <aside className="sticky top-24 rounded-xl border border-surface-variant bg-surface-container-lowest p-md shadow-card">
      <h2 className="mb-md border-b border-surface-variant pb-xs text-headline-sm">
        Your preferences
      </h2>
      <form className="space-y-sm" onSubmit={handleSubmit(submitHandler)} noValidate>
        <LocationSelect
          locations={locations}
          value={location}
          onChange={(v) => setValue("location", v, { shouldValidate: true })}
          disabled={disabled || locations.length === 0}
          error={errors.location?.message}
        />

        <BudgetSelector
          value={budget as BudgetBand}
          onChange={(v) => setValue("budget", v)}
          disabled={disabled}
        />

        <CuisineSelect
          cuisines={cuisines}
          value={cuisine}
          onChange={(v) => setValue("cuisine", v, { shouldValidate: true })}
          disabled={disabled || cuisines.length === 0}
          error={errors.cuisine?.message}
        />

        <RatingSlider
          value={minRating}
          onChange={(v) => setValue("min_rating", v)}
          disabled={disabled}
        />

        <div>
          <label
            htmlFor="additional-preferences"
            className="mb-xs block text-label-sm uppercase tracking-wider text-on-surface-variant"
          >
            Vibe &amp; Details (Optional)
          </label>
          <textarea
            id="additional-preferences"
            {...register("additional_preferences")}
            disabled={disabled}
            placeholder="e.g. romantic, live music, fast service"
            className="min-h-[80px] w-full resize-none rounded-lg border border-surface-variant bg-surface-container-lowest p-sm text-body-md transition-colors focus:border-primary-brand focus:outline-none focus:ring-1 focus:ring-primary-brand/10"
          />
          <div className="mt-1 flex justify-between text-label-md text-on-surface-variant">
            {errors.additional_preferences && (
              <span className="text-red-600">{errors.additional_preferences.message}</span>
            )}
            <span className="ml-auto">{additionalPreferences.length} / 500</span>
          </div>
        </div>

        <div>
          <label
            htmlFor="top-n"
            className="mb-xs block text-label-sm uppercase tracking-wider text-on-surface-variant"
          >
            Number of Results
          </label>
          <div className="flex items-center gap-sm">
            <button
              type="button"
              disabled={disabled || topN <= 1}
              onClick={() => setValue("top_n", Math.max(1, topN - 1))}
              className="flex h-11 w-11 items-center justify-center rounded-lg border border-surface-variant text-on-surface-variant transition-colors hover:border-primary-brand disabled:opacity-40"
              aria-label="Decrease number of results"
            >
              <Icon name="remove" className="text-[18px]" />
            </button>
            <span className="min-w-[2rem] text-center text-headline-sm" aria-live="polite">
              {topN}
            </span>
            <button
              type="button"
              disabled={disabled || topN >= 10}
              onClick={() => setValue("top_n", Math.min(10, topN + 1))}
              className="flex h-11 w-11 items-center justify-center rounded-lg border border-surface-variant text-on-surface-variant transition-colors hover:border-primary-brand disabled:opacity-40"
              aria-label="Increase number of results"
            >
              <Icon name="add" className="text-[18px]" />
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={disabled}
          className={cn(
            "mt-md flex min-h-[44px] w-full items-center justify-center gap-sm rounded-lg bg-primary-brand py-sm text-headline-sm text-white shadow-md transition-all",
            "hover:bg-primary-hover active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60",
          )}
        >
          {isSubmitting ? (
            <>
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Finding recommendations...
            </>
          ) : (
            <>
              <Icon name="auto_awesome" className="text-[20px]" />
              Get AI Recommendations
            </>
          )}
        </button>
      </form>
    </aside>
  );
}
