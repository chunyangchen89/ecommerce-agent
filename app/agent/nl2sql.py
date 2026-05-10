import logging

from langfuse.decorators import observe
from openai import OpenAI
from sqlalchemy import text

from app.agent.state import AgentState
from app.config import settings
from app.data_generator.ddl import get_ddl_for_tables
from app.db.milvus import get_milvus_client
from app.db.postgres import sync_engine
from app.embedding.client import embed_texts

logger = logging.getLogger(__name__)

SQL_PROMPT = """你是一个PostgreSQL SQL生成器。根据以下表结构和用户问题，生成一条SQL查询。

规则：
- 只生成 SELECT 语句
- 使用正确的 JOIN 语法
- 使用中文列注释理解列含义
- 只返回SQL，不要解释

表结构：
{ddl}

用户问题：{query}"""


@observe(name="table_discovery")
def table_discovery(query: str, top_k: int = 3) -> list[str]:
    client = get_milvus_client()
    client.load_collection("table_metadata")
    vecs = embed_texts([query])
    if not vecs:
        return []
    results = client.search(
        collection_name="table_metadata",
        data=[vecs[0]],
        limit=top_k,
        output_fields=["table_name"],
    )
    return [r["entity"]["table_name"] for r in results[0]]


@observe(name="sql_generation", as_type="generation")
def generate_sql(query: str, ddl: str) -> str:
    client = OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key="ollama")
    prompt = SQL_PROMPT.format(ddl=ddl, query=query)
    resp = client.chat.completions.create(
        model=settings.OLLAMA_LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    sql = resp.choices[0].message.content.strip()
    # Strip markdown code blocks if present
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[-1]
        if sql.endswith("```"):
            sql = sql[:-3]
        sql = sql.strip()
    return sql


def _execute_sql(sql: str) -> list[dict]:
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return []

    with sync_engine.connect() as conn:
        result = conn.execute(text(sql))
        cols = list(result.keys())
        rows = result.fetchall()
        if not rows:
            return []

        return [dict(zip(cols, row)) for row in rows[:50]]


@observe(name="nl2sql")
def nl2sql_node(state: AgentState) -> dict:
    query = state["query"]

    # Step 1: discover relevant tables
    tables = table_discovery(query)
    logger.info(f"Table discovery for '{query[:50]}...': {tables}")

    # Step 2: load DDL
    ddl = get_ddl_for_tables(tables)

    # Step 3: generate SQL
    sql = generate_sql(query, ddl)
    logger.info(f"Generated SQL:\n{sql}")

    # Step 4: execute
    sql_result = _execute_sql(sql)

    return {
        "relevant_tables": tables,
        "ddl_schema": ddl,
        "sql": sql,
        "sql_result": sql_result,
    }
