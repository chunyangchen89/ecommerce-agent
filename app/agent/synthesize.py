import logging

from langfuse.decorators import observe
from openai import OpenAI

from app.agent.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

SYNTHESIZE_PROMPT = """你是一个电商数据分析师。根据以下数据回答用户问题。

## 结构化查询结果
{sql_result}

## 非结构化分析（用户评价）
{rag_context}

## 用户问题
{query}

请给出清晰、可操作的分析回答。

规则：
- 不要用表格重复展示上面的结构化查询结果，数据表格会由系统单独渲染
- 直接用要点列表和文字进行分析说明
- 如果有评价洞察，归纳关键主题和原因
- 结合结构化数据和非结构化评价给出综合分析"""


def _format_rows_as_table(rows: list[dict]) -> str:
    if not rows:
        return "无结构化数据"
    cols = list(rows[0].keys())
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    body = "\n".join(
        "| " + " | ".join(str(row.get(c, "")) for c in cols) + " |"
        for row in rows
    )
    return f"{header}\n{sep}\n{body}"


@observe(name="synthesize", as_type="generation")
def synthesize_node(state: AgentState) -> dict:
    client = OpenAI(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
    prompt = SYNTHESIZE_PROMPT.format(
        sql_result=_format_rows_as_table(state.get("sql_result") or []),
        rag_context=state.get("rag_context") or "无评价数据",
        query=state["query"],
    )

    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    answer = resp.choices[0].message.content.strip()
    return {"final_answer": answer}
