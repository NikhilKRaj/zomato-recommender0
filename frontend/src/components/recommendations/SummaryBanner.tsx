import { Icon } from "@/components/ui/Icon";

interface SummaryBannerProps {
  summary: string;
}

export function SummaryBanner({ summary }: SummaryBannerProps) {
  return (
    <div className="flex items-start gap-sm rounded-xl border border-ai-banner-border bg-ai-banner p-md shadow-sm">
      <Icon name="auto_awesome" className="ai-sparkle mt-1 flex-shrink-0 text-[24px]" />
      <p className="text-body-md leading-relaxed text-on-surface">{summary}</p>
    </div>
  );
}
