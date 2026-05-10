import logging

from langchain_openai import ChatOpenAI
from langfuse.decorators import observe

from app.agent.state import AgentState, CollectionType, IntentResponse
from app.config import settings

logger = logging.getLogger(__name__)


INTENT_PROMPT = """你是一个查询分类器。根据用户问题判断查询意图和需要检索的集合。

意图类型：
- "nl2sql": 需要结构化数据查询（数量、比例、排名、趋势、对比）
- "rag": 需要非结构化分析（评价、反馈、原因分析、用户感受）
- "hybrid": 同时需要以上两者

集合类型：
- "table_metadata": 表结构元数据（用于发现相关的数据库表）
- "ecommerce_products": 商品信息（名称、类别、品牌、价格、评分）
- "reviews_sku": 用户评价和反馈（评价文本、评分、退货原因）

用户问题: {query}"""

_structured_llm = (
    ChatOpenAI(
        base_url=settings.OLLAMA_BASE_URL,
        api_key="ollama",
        model=settings.OLLAMA_LLM_MODEL,
        temperature=0,
    )
    .with_structured_output(IntentResponse, method="function_calling")
)


@observe(name="intent_router")
def intent_router_node(state: AgentState) -> dict:
    prompt = INTENT_PROMPT.format(query=state["query"])
    result: IntentResponse = _structured_llm.invoke(prompt)
    logger.info(
        f"Intent for '{state['query'][:50]}...': {result.intent}, "
        f"collections: {[c.value for c in result.rag_collections]}"
    )
    return {"intent": result.intent, "rag_collections": result.rag_collections}
