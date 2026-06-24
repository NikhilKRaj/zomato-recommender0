import type { RecommendationResponse } from "@/api/types";
import { Icon } from "@/components/ui/Icon";

import { RecommendationCard } from "./RecommendationCard";
import { SummaryBanner } from "./SummaryBanner";

interface ResultsListProps {
  data: RecommendationResponse;
}

export function ResultsList({ data }: ResultsListProps) {
  const { summary, recommendations, meta } = data;

  return (
    <section className="flex flex-col gap-md" aria-live="polite">
      {summary && <SummaryBanner summary={summary} />}

      <div className="flex flex-wrap items-center gap-xs text-label-md text-on-surface-variant">
        <span className="flex items-center gap-1">
          <Icon name="database" className="text-[16px]" />
          {meta.candidates_considered} restaurants considered
        </span>
        <span>·</span>
        <span className="flex items-center gap-1">
          <Icon name="sort" className="text-[16px]" />
          {meta.source === "fallback" ? "Ranked by rating" : "Ranked by AI"}
        </span>
        {meta.source === "fallback" && (
          <>
            <span>·</span>
            <span className="rounded-full bg-amber/20 px-2 py-0.5 text-label-sm text-amber">
              Fallback ranking
            </span>
          </>
        )}
      </div>

      <div className="flex flex-col gap-md">
        {recommendations.map((rec) => (
          <RecommendationCard key={rec.restaurant.id} recommendation={rec} />
        ))}
      </div>
    </section>
  );
}
