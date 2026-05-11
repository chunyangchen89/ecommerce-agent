"use client";

import { useHealthCheck } from "@/hooks/use-health-check";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";

const services = [
  { key: "postgres" as const, label: "PostgreSQL" },
  { key: "milvus" as const, label: "Milvus" },
  { key: "redis" as const, label: "Redis" },
  { key: "langfuse" as const, label: "Langfuse" },
];

export function HealthBadge() {
  const health = useHealthCheck();

  return (
    <div className="flex items-center gap-2">
      {services.map((s) => {
        const ok = health ? health[s.key] : null;
        return (
          <Tooltip key={s.key}>
            <TooltipTrigger className="p-0 border-0 bg-transparent">
              <div
                className={`h-2 w-2 rounded-full ${
                  ok === null
                    ? "bg-stone"
                    : ok
                      ? "bg-meta-success"
                      : "bg-meta-critical"
                }`}
              />
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              {s.label}:{" "}
              {ok === null ? "checking..." : ok ? "connected" : "disconnected"}
            </TooltipContent>
          </Tooltip>
        );
      })}
      {health && (
        <Badge
          variant="secondary"
          className={`rounded-full px-2 py-0 text-[11px] font-bold ${
            health.status === "healthy"
              ? "bg-meta-success text-white"
              : "bg-meta-attention text-white"
          }`}
        >
          {health.status === "healthy" ? "Operational" : "Degraded"}
        </Badge>
      )}
    </div>
  );
}
