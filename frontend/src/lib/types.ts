export interface QueryRequest {
  query: string;
  top_k?: number;
}

export interface QueryResponse {
  answer: string;
  intent: "nl2sql" | "rag" | "hybrid" | "";
  sql: string | null;
  sql_result: Record<string, unknown>[] | null;
  rag_context: string | null;
}

export interface HealthResponse {
  status: "healthy" | "degraded";
  postgres: boolean;
  milvus: boolean;
  redis: boolean;
  langfuse: boolean;
}
