import { Icon } from "@/components/ui/Icon";

export function Footer() {
  return (
    <footer className="mt-xl w-full border-t border-outline-variant bg-surface-container-low py-lg">
      <div className="mx-auto flex w-full max-w-container flex-col items-center justify-between gap-4 px-margin-mobile text-body-md md:flex-row md:px-margin-desktop">
        <div className="text-headline-sm text-on-surface">
          © {new Date().getFullYear()} DineAI. All rights reserved.
        </div>
        <div className="flex items-center gap-2 text-sm text-on-surface-variant">
          <span>Data from Zomato</span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <Icon name="memory" className="text-[14px]" />
            Powered by Groq AI
          </span>
        </div>
      </div>
    </footer>
  );
}
