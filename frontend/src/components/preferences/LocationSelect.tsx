import { cn } from "@/lib/utils";

interface LocationSelectProps {
  locations: string[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: string;
}

export function LocationSelect({
  locations,
  value,
  onChange,
  disabled,
  error,
}: LocationSelectProps) {
  return (
    <div>
      <label
        htmlFor="location"
        className="mb-xs block text-label-sm uppercase tracking-wider text-on-surface-variant"
      >
        Location
      </label>
      <div className="relative">
        <span className="material-symbols-outlined pointer-events-none absolute left-sm top-1/2 -translate-y-1/2 text-on-surface-variant">
          location_on
        </span>
        <select
          id="location"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={error ? "location-error" : undefined}
          className={cn(
            "w-full appearance-none rounded-lg border bg-surface-container-lowest py-sm pl-xl pr-8 text-body-md transition-colors",
            "focus:border-primary-brand focus:outline-none focus:ring-1 focus:ring-primary-brand/10",
            error ? "border-red-500" : "border-surface-variant",
            disabled && "cursor-not-allowed opacity-60",
          )}
        >
          <option value="">Select a neighbourhood</option>
          {locations.map((location) => (
            <option key={location} value={location}>
              {location}
            </option>
          ))}
        </select>
        <span className="material-symbols-outlined pointer-events-none absolute right-sm top-1/2 -translate-y-1/2 text-on-surface-variant">
          expand_more
        </span>
      </div>
      {error && (
        <p id="location-error" className="mt-1 text-label-md text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
