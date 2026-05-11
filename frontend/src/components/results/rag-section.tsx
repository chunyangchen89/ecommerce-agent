"use client";

import { useState } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { FileText } from "lucide-react";

interface RagSectionProps {
  context: string;
}

export function RagSection({ context }: RagSectionProps) {
  const [open, setOpen] = useState(false);

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex w-full items-center justify-between rounded-xl p-3 hover:bg-surface-soft transition-colors">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-steel" />
          <span className="text-sm font-bold text-ink-deep">RAG Context</span>
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
        <div className="mx-3 mb-3 max-h-80 overflow-y-auto whitespace-pre-wrap rounded-2xl bg-surface-soft p-4 text-sm text-charcoal">
          {context}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
