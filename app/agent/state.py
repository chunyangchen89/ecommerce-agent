from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel


class IntentType(StrEnum):
    NL2SQL = "nl2sql"
    RAG = "rag"
    HYBRID = "hybrid"


class CollectionType(StrEnum):
    TABLE_METADATA = "table_metadata"
    ECOMMERCE_PRODUCTS = "ecommerce_products"
    REVIEWS_SKU = "reviews_sku"


class IntentResponse(BaseModel):
    intent: IntentType
    rag_collections: list[CollectionType]


class AgentState(TypedDict):
    query: str
    intent: IntentType
    rag_collections: list[CollectionType]
    relevant_tables: list[str]
    ddl_schema: str
    sql: str | None
    sql_result: list[dict] | None
    rag_context: str | None
    final_answer: str
