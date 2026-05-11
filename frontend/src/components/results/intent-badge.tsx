import { Badge } from "@/components/ui/badge";

interface IntentBadgeProps {
  intent: string;
}

export function IntentBadge({ intent }: IntentBadgeProps) {
  const variants: Record<string, string> = {
    nl2sql: "bg-surface-soft text-ink-deep border-hairline",
    rag: "bg-cobalt/10 text-cobalt border-cobalt/20",
    hybrid: "bg-cobalt text-white border-cobalt",
  };

  const cls = variants[intent] ?? "bg-surface-soft text-steel border-hairline";

  return (
    <Badge
      variant="outline"
      className={`rounded-full px-3 py-0.5 text-xs font-bold ${cls}`}
    >
      {intent.toUpperCase()}
    </Badge>
  );
}
