import { cn } from "@/lib/utils";

interface IconProps {
  name: string;
  className?: string;
  filled?: boolean;
}

export function Icon({ name, className, filled }: IconProps) {
  return (
    <span
      className={cn(
        "material-symbols-outlined",
        filled && "star-filled",
        className,
      )}
      aria-hidden="true"
    >
      {name}
    </span>
  );
}
