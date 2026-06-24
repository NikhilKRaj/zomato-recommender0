import { useRef } from "react";

import { ApiClientError, getErrorMessage } from "@/api/client";
import type { UserPreferences } from "@/api/types";
import { PageShell } from "@/components/layout/PageShell";
import { PreferenceForm } from "@/components/preferences/PreferenceForm";
import { EmptyState } from "@/components/recommendations/EmptyState";
import { LoadingSkeleton } from "@/components/recommendations/LoadingSkeleton";
import { ResultsList } from "@/components/recommendations/ResultsList";
import { useMetadata } from "@/hooks/useMetadata";
import { useRecommendations } from "@/hooks/useRecommendations";

export function HomePage() {
  const resultsRef = useRef<HTMLElement>(null);
  const formRef = useRef<HTMLDivElement>(null);
  const metadata = useMetadata();
  const recommendations = useRecommendations();

  const handleSubmit = (preferences: UserPreferences) => {
    recommendations.mutate(preferences, {
      onSuccess: () => {
        requestAnimationFrame(() => {
          resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      },
    });
  };

  const isNotFound =
    recommendations.error instanceof ApiClientError && recommendations.error.status === 404;

  const showResults =
    recommendations.isSuccess && recommendations.data.recommendations.length > 0;

  return (
    <PageShell>
      <section className="mb-xl max-w-3xl text-center md:text-left">
        <h1 className="mb-sm text-headline-lg-mobile text-on-surface md:text-headline-lg">
          Find your perfect restaurant in Bangalore
        </h1>
        <p className="text-body-lg text-on-surface-variant">
          Tell us what you&apos;re craving. Our AI ranks real restaurants and explains why each
          one fits.
        </p>
      </section>

      {metadata.isError && (
        <div className="mb-md rounded-lg border border-red-200 bg-red-50 p-sm text-body-md text-red-800" role="alert">
          {getErrorMessage(
            metadata.error,
            "Could not load filter options. Redeploy Vercel and confirm Railway is running.",
          )}
        </div>
      )}

      <div ref={formRef} className="grid grid-cols-1 items-start gap-lg md:grid-cols-[380px_1fr]">
        <PreferenceForm
          locations={metadata.locations}
          cuisines={metadata.cuisines}
          isLoading={metadata.isLoading}
          isSubmitting={recommendations.isPending}
          onSubmit={handleSubmit}
        />

        <section ref={resultsRef} className="min-h-[200px]">
          {recommendations.isPending && <LoadingSkeleton />}

          {showResults && recommendations.data && (
            <ResultsList data={recommendations.data} />
          )}

          {isNotFound && (
            <EmptyState
              onAdjustFilters={() => {
                formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            />
          )}

          {recommendations.isError && !isNotFound && (
            <div
              className="rounded-xl border border-red-200 bg-red-50 p-md text-body-md text-red-800"
              role="alert"
            >
              {getErrorMessage(recommendations.error, "Something went wrong. Please try again.")}
            </div>
          )}

          {!recommendations.isPending &&
            !showResults &&
            !recommendations.isError &&
            !metadata.isLoading && (
              <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-surface-variant bg-surface-container-lowest p-xl text-center">
                <span className="material-symbols-outlined ai-sparkle mb-sm text-[40px]">
                  auto_awesome
                </span>
                <p className="text-body-lg text-on-surface-variant">
                  Set your preferences and tap &ldquo;Get AI Recommendations&rdquo; to see your
                  personalized picks.
                </p>
              </div>
            )}
        </section>
      </div>
    </PageShell>
  );
}
