export function LoadingSkeleton() {
  return (
    <section className="flex flex-col gap-md" aria-busy="true" aria-label="Loading recommendations">
      <p className="text-body-md text-on-surface-variant">AI is ranking restaurants for you...</p>
      <div className="h-20 animate-pulse rounded-xl bg-surface-container" />
      <div className="flex flex-col gap-md">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse rounded-xl border border-surface-variant bg-surface-container-lowest p-md"
          >
            <div className="mb-sm h-6 w-1/3 rounded bg-surface-container" />
            <div className="mb-sm h-4 w-2/3 rounded bg-surface-container" />
            <div className="h-16 rounded-lg bg-surface-container" />
          </div>
        ))}
      </div>
    </section>
  );
}
