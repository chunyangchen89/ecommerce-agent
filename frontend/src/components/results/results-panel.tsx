import type { QueryResponse } from "@/lib/types";
import { IntentBadge } from "./intent-badge";
import { AnswerCard } from "./answer-card";
import { SqlSection } from "./sql-section";
import { DataTable } from "./data-table";
import { RagSection } from "./rag-section";

interface ResultsPanelProps {
  data: QueryResponse;
}

export function ResultsPanel({ data }: ResultsPanelProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      {data.intent && <IntentBadge intent={data.intent} />}
      <AnswerCard answer={data.answer} />
      {data.sql && <SqlSection sql={data.sql} />}
      {data.sql_result && data.sql_result.length > 0 && (
        <DataTable data={data.sql_result} />
      )}
      {data.rag_context && <RagSection context={data.rag_context} />}
    </div>
  );
}
