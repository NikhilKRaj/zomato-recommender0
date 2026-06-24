import type { ReactNode } from "react";

import { Footer } from "./Footer";
import { Header } from "./Header";

interface PageShellProps {
  children: ReactNode;
}

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="mx-auto w-full max-w-container flex-1 px-margin-mobile pb-lg pt-24 md:px-margin-desktop">
        {children}
      </main>
      <Footer />
    </div>
  );
}
