import type { BudgetBand } from "@/api/types";
import { cn } from "@/lib/utils";

const BUDGET_OPTIONS: Array<{
  value: BudgetBand;
  label: string;
  hint: string;
}> = [
  { value: "low", label: "Low", hint: "₹0–300" },
  { value: "medium", label: "Medium", hint: "₹301–600" },
  { value: "high", label: "High", hint: "₹601+" },
];

interface BudgetSelectorProps {
  value: BudgetBand;
  onChange: (value: BudgetBand) => void;
  disabled?: boolean;
}

export function BudgetSelector({ value, onChange, disabled }: BudgetSelectorProps) {
  return (
    <div>
      <span className="mb-xs block text-label-sm uppercase tracking-wider text-on-surface-variant">
        Budget (For Two)
      </span>
      <div className="grid grid-cols-3 gap-xs" role="radiogroup" aria-label="Budget">
        {BUDGET_OPTIONS.map((option) => {
          const selected = value === option.value;
          return (
            <label
              key={option.value}
              className={cn("cursor-pointer", disabled && "cursor-not-allowed opacity-60")}
            >
              <input
                type="radio"
                name="budget"
                value={option.value}
                checked={selected}
                onChange={() => onChange(option.value)}
                disabled={disabled}
                className="peer sr-only"
              />
              <div
                className={cn(
                  "rounded-lg border py-xs text-center text-label-md transition-colors",
                  selected
                    ? "border-primary-brand bg-primary-brand/5 text-primary-brand shadow-sm"
                    : "border-surface-variant text-on-surface-variant peer-checked:border-primary-brand peer-checked:bg-primary-brand/5 peer-checked:text-primary-brand",
                )}
              >
                {option.label}
                <br />
                <span className="text-[10px] font-normal">{option.hint}</span>
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
}
