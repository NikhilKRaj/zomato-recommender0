import type { Recommendation } from "@/api/types";
import { Icon } from "@/components/ui/Icon";
import { cn, formatCost, formatRating } from "@/lib/utils";

interface RecommendationCardProps {
  recommendation: Recommendation;
  isTopPick?: boolean;
}

export function RecommendationCard({ recommendation, isTopPick }: RecommendationCardProps) {
  const { rank, restaurant, explanation } = recommendation;
  const topPick = isTopPick ?? rank === 1;

  return (
    <article
      className={cn(
        "relative overflow-hidden rounded-xl border bg-surface-container-lowest transition-all duration-300",
        topPick
          ? "border-2 border-primary-brand shadow-card-hover"
          : "border-surface-variant shadow-card hover:-translate-y-1 hover:shadow-card-hover",
      )}
    >
      <div
        className={cn(
          "absolute left-0 top-0 z-10 flex items-center gap-1 rounded-br-lg px-sm py-1 text-label-sm font-bold",
          topPick
            ? "bg-primary-brand text-white"
            : "bg-surface-container-high font-medium text-on-surface-variant",
        )}
      >
        {topPick ? `#${rank} Match` : `#${rank}`}
      </div>

      <div className="flex flex-col p-md pt-8">
        <div className="mb-sm">
          <div className="mb-xs flex items-start justify-between">
            <h3 className="text-headline-md text-on-surface">{restaurant.name}</h3>
          </div>

          <div className="mb-sm flex flex-wrap items-center gap-sm text-body-md text-on-surface-variant">
            <span className="flex items-center gap-1 font-medium text-on-surface">
              <Icon name="star" className="star-filled text-[18px]" filled />
              {formatRating(restaurant.rating)}
            </span>
            <span>•</span>
            <span>{restaurant.cuisines.join(", ")}</span>
            <span>•</span>
            <span>{formatCost(restaurant.cost_for_two)}</span>
          </div>

          {restaurant.location && (
            <div className="mb-sm flex items-center gap-1 text-body-md text-on-surface-variant">
              <Icon name="location_on" className="text-[16px]" />
              <span>{restaurant.location}</span>
            </div>
          )}

          {restaurant.cuisines.length > 0 && (
            <div className="mb-sm flex flex-wrap gap-xs">
              {restaurant.cuisines.slice(0, 4).map((c) => (
                <span
                  key={c}
                  className="rounded-full bg-surface-container-high px-xs py-1 text-label-sm text-on-surface-variant"
                >
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-lg border border-surface-variant bg-surface-container-low p-sm">
          <p className="flex items-start gap-2 text-sm text-on-surface">
            <Icon name="tips_and_updates" className="mt-0.5 text-[16px] text-primary-brand" />
            <span className="italic text-on-surface-variant">&ldquo;{explanation}&rdquo;</span>
          </p>
        </div>

        {restaurant.url && (
          <a
            href={restaurant.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-sm inline-flex min-h-[44px] items-center justify-center gap-1 rounded-lg border border-surface-variant px-md py-xs text-body-md text-on-surface-variant transition-colors hover:border-primary-brand hover:text-primary-brand"
          >
            View on Zomato
            <Icon name="open_in_new" className="text-[16px]" />
          </a>
        )}
      </div>
    </article>
  );
}
