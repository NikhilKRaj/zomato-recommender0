import { Icon } from "@/components/ui/Icon";

interface EmptyStateProps {
  onAdjustFilters?: () => void;
}

export function EmptyState({ onAdjustFilters }: EmptyStateProps) {
  return (
    <section
      className="flex flex-col items-center rounded-xl border border-surface-variant bg-surface-container-lowest p-xl text-center shadow-card"
      role="status"
    >
      <div className="mb-md flex h-16 w-16 items-center justify-center rounded-full bg-surface-container">
        <Icon name="search_off" className="text-[32px] text-on-surface-variant" />
      </div>
      <h3 className="mb-sm text-headline-md text-on-surface">No restaurants match your filters</h3>
      <p className="mb-md max-w-md text-body-md text-on-surface-variant">
        Try broadening your search — relax your minimum rating, pick a nearby neighbourhood, or
        choose a different cuisine.
      </p>
      {onAdjustFilters && (
        <button
          type="button"
          onClick={onAdjustFilters}
          className="min-h-[44px] rounded-lg border border-surface-variant px-lg py-sm text-body-md text-on-surface-variant transition-colors hover:border-primary-brand hover:text-primary-brand"
        >
          Adjust filters
        </button>
      )}
    </section>
  );
}
