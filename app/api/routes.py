import asyncio
import logging

from fastapi import APIRouter
from langfuse.decorators import langfuse_context

from app.agent.graph import build_agent_graph
from app.db.langfuse import init_langfuse, is_langfuse_configured
from app.db.milvus import get_milvus_client
from app.db.redis import get_redis
from app.models.schemas import HealthResponse, QueryRequest, QueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    init_langfuse()

    graph = build_agent_graph()
    initial_state = {
        "query": req.query,
        "intent": "",
        "rag_collections": [],
        "relevant_tables": [],
        "ddl_schema": "",
        "sql": None,
        "sql_result": None,
        "rag_context": None,
        "final_answer": "",
    }

    if is_langfuse_configured():
        langfuse_context.update_current_trace(
            name="query",
            input={"query": req.query},
        )

    result = await asyncio.to_thread(graph.invoke, initial_state)

    if is_langfuse_configured():
        langfuse_context.update_current_trace(
            output={"intent": result.get("intent", ""), "answer": result["final_answer"][:500]},
        )

    return QueryResponse(
        answer=result["final_answer"],
        intent=result.get("intent", ""),
        sql=result.get("sql"),
        sql_result=result.get("sql_result"),
        rag_context=result.get("rag_context"),
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    pg_ok = False
    milvus_ok = False
    redis_ok = False
    langfuse_ok = False

    try:
        from app.db.postgres import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        pg_ok = True
    except Exception:
        pass

    try:
        client = get_milvus_client()
        client.list_collections()
        milvus_ok = True
    except Exception:
        pass

    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        pass

    if is_langfuse_configured():
        try:
            langfuse_ok = bool(langfuse_context.auth_check())
        except Exception:
            pass

    status = "healthy" if all([pg_ok, milvus_ok, redis_ok, langfuse_ok]) else "degraded"
    return HealthResponse(
        status=status,
        postgres=pg_ok,
        milvus=milvus_ok,
        redis=redis_ok,
        langfuse=langfuse_ok,
    )
