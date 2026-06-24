import { Icon } from "@/components/ui/Icon";

export function Header() {
  return (
    <header className="fixed top-0 z-50 w-full border-b border-surface-variant bg-surface/80 shadow-sm backdrop-blur-md">
      <div className="mx-auto flex h-16 w-full max-w-container items-center justify-between px-margin-mobile md:px-margin-desktop">
        <div className="text-headline-md font-extrabold text-primary">DineAI</div>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1 rounded-full bg-surface-variant px-sm py-1 text-label-sm text-on-surface-variant">
            <Icon name="bolt" className="text-[14px]" />
            Powered by AI
          </span>
        </div>
      </div>
    </header>
  );
}
