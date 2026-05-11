"use client";

import { useState } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { Code, Copy, Check } from "lucide-react";

interface SqlSectionProps {
  sql: string;
}

export function SqlSection({ sql }: SqlSectionProps) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  async function copySql() {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex w-full items-center justify-between rounded-xl p-3 hover:bg-surface-soft transition-colors">
        <div className="flex items-center gap-2">
          <Code className="h-4 w-4 text-steel" />
          <span className="text-sm font-bold text-ink-deep">
            Generated SQL
          </span>
        </div>
        <svg
          className={`h-4 w-4 text-steel transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="relative mx-3 mb-3">
          <pre className="overflow-x-auto rounded-2xl bg-surface-soft p-4 text-sm text-charcoal">
            <code>{sql}</code>
          </pre>
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-2 top-2 h-8 w-8"
            onClick={copySql}
          >
            {copied ? (
              <Check className="h-4 w-4 text-meta-success" />
            ) : (
              <Copy className="h-4 w-4 text-steel" />
            )}
          </Button>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
