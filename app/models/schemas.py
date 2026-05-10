from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    top_k: int = 10


class QueryResponse(BaseModel):
    answer: str
    intent: str
    sql: str | None = None
    sql_result: list[dict] | None = None
    rag_context: str | None = None


class HealthResponse(BaseModel):
    status: str
    postgres: bool
    milvus: bool
    redis: bool
    langfuse: bool = False
