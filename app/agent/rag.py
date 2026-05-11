import logging

from langfuse.decorators import observe
from llama_index.core import Settings as LISettings, VectorStoreIndex
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore
from pymilvus import MilvusClient

from app.agent.state import AgentState, CollectionType
from app.config import settings
from app.embedding.client import embed_texts

logger = logging.getLogger(__name__)


# Configure LlamaIndex to use Ollama embeddings
LISettings.embed_model = OpenAIEmbedding(
    model_name=settings.OLLAMA_EMBED_MODEL,
    api_base=settings.OLLAMA_BASE_URL,
    api_key="ollama",
    embed_batch_size=20,
)

_reranker_llm = LlamaOpenAI(
    model_name=settings.OLLAMA_LLM_MODEL,
    api_base=settings.OLLAMA_BASE_URL,
    api_key="ollama",
    temperature=0.0,
)


def _llamaindex_search(collection_name: str, query: str, filters: MetadataFilters | None = None, top_k: int = 20) -> list[str]:
    vector_store = MilvusVectorStore(
        uri=settings.MILVUS_URI,
        collection_name=collection_name,
        dim=settings.OLLAMA_EMBED_DIM,
        text_key="text",
        embedding_field="vector",
        overwrite=False,
    )
    index = VectorStoreIndex.from_vector_store(vector_store)
    reranker = LLMRerank(llm=_reranker_llm, top_n=5)

    retriever_kwargs = {"similarity_top_k": top_k, "node_postprocessors": [reranker]}
    if filters:
        retriever_kwargs["filters"] = filters

    retriever = index.as_retriever(**retriever_kwargs)
    nodes = retriever.retrieve(query)

    results = []
    for node in nodes:
        meta = node.metadata
        content = node.text or node.get_content() or ""
        label = meta.get("title", meta.get("sku", ""))
        if not label and content:
            label = content.split("\n")[0][:60]
        results.append(
            "- [%.4f] %s | %s" % (
                node.score,
                label,
                content[:200],
            )
        )
    return results


def _get_scalar_fields(client: MilvusClient, collection_name: str) -> list[str]:
    """Introspect collection schema, return non-vector, non-primary field names."""
    info = client.describe_collection(collection_name)
    return [
        f["name"] for f in info["fields"]
        if not f.get("is_primary") and f["type"] != "FloatVector"
    ]


def _pymilvus_search(collection_name: str, query: str, filter_expr: str = "", top_k: int = 10) -> list[str]:
    client = MilvusClient(uri=settings.MILVUS_URI)
    client.load_collection(collection_name)

    output_fields = _get_scalar_fields(client, collection_name)

    vecs = embed_texts([query])
    if not vecs:
        client.close()
        return []

    results = client.search(
        collection_name=collection_name,
        data=[vecs[0]],
        filter=filter_expr,
        limit=top_k,
        output_fields=output_fields,
        search_params={"metric_type": "COSINE", "params": {"ef": 128}},
    )

    formatted = []
    if results and results[0]:
        for hit in results[0]:
            e = hit["entity"]
            label = e.get("title") or e.get("sku", "")
            body = str(e.get("text", ""))[:200]
            formatted.append("- [%.4f] %s | %s" % (hit["distance"], label, body))
    client.close()
    return formatted


@observe(name="rag")
def rag_node(state: AgentState) -> dict:
    query = state["query"]
    collections = state.get("rag_collections", [CollectionType.ECOMMERCE_PRODUCTS])

    # Build filters from NL2SQL results if available
    skus: list[str] = []
    sql_result = state.get("sql_result") or []
    if sql_result and "sku" in sql_result[0]:
        skus = list({row["sku"] for row in sql_result if row.get("sku")})[:20]
        if skus:
            logger.info("RAG filtering by SKUs from NL2SQL: %s", skus)

    all_results: list[str] = []
    for coll in collections:
        # Only search data collections, skip table_metadata (used by NL2SQL)
        if coll == CollectionType.TABLE_METADATA:
            continue

        # Build filters for this collection
        filters = None
        if skus and coll == CollectionType.REVIEWS_SKU:
            filters = MetadataFilters(filters=[
                MetadataFilter(key="sku", value=skus, operator="in"),
            ])

        # Strategy A: LlamaIndex retriever
        try:
            results = _llamaindex_search(coll.value, query, filters=filters)
            if results:
                all_results.extend(results)
                continue
        except Exception as e:
            logger.warning("LlamaIndex search failed for %s, trying pymilvus: %s", coll.value, e)

        # Strategy B: pymilvus fallback
        filter_expr = ""
        if filters:
            for f in filters.filters:
                if f.operator == "in" and f.key == "sku":
                    vals = '", "'.join(f.value)
                    filter_expr = 'sku in ["%s"]' % vals

        results = _pymilvus_search(coll.value, query, filter_expr=filter_expr)
        if results:
            all_results.extend(results)

    context = "\n".join(all_results) if all_results else "No relevant documents found."
    return {"rag_context": context}
