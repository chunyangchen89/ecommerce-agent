"use client";

import { HealthBadge } from "./health-badge";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-hairline-soft bg-canvas">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-5">
        <span className="text-lg font-bold text-ink-deep">Data Agent</span>
        <HealthBadge />
      </div>
    </header>
  );
}
