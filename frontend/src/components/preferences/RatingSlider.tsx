import { Icon } from "@/components/ui/Icon";
import { formatRating } from "@/lib/utils";

interface RatingSliderProps {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export function RatingSlider({ value, onChange, disabled }: RatingSliderProps) {
  return (
    <div>
      <div className="mb-xs flex items-center justify-between">
        <label htmlFor="min-rating" className="text-label-sm uppercase tracking-wider text-on-surface-variant">
          Minimum Rating
        </label>
        <span className="flex items-center text-label-md text-amber">
          <Icon name="star" className="star-filled mr-1 text-[16px]" filled />
          {formatRating(value)}
        </span>
      </div>
      <input
        id="min-rating"
        type="range"
        min={0}
        max={5}
        step={0.5}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        disabled={disabled}
        className="slider-thumb"
        aria-valuemin={0}
        aria-valuemax={5}
        aria-valuenow={value}
      />
      <div className="mt-1 flex justify-between text-[10px] text-on-surface-variant">
        <span>0.0</span>
        <span>5.0</span>
      </div>
    </div>
  );
}
