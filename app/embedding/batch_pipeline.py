import logging
import math
import time
from typing import TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy import text
from tqdm import tqdm

from app.config import settings
from app.db.milvus import get_milvus_client
from app.db.postgres import sync_engine
from app.embedding.checkpoint import CheckpointManager
from app.embedding.client import embed_texts, validate_embedding
from app.embedding.milvus_collections import create_products_collection, create_reviews_collection

logger = logging.getLogger(__name__)


class BatchState(TypedDict):
    collection_name: str
    total_records: int
    chunk_index: int
    total_chunks: int
    processed_count: int
    skipped_count: int
    failed_count: int
    failed_ids: list[str]
    start_time: float
    rows: list[dict]


def _count_table(table_name: str) -> int:
    with sync_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM " + table_name))
        return result.scalar_one()


def _read_chunk(table_name: str, offset: int, limit: int) -> list[dict]:
    with sync_engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM " + table_name + " LIMIT :limit OFFSET :offset"),
            {"limit": limit, "offset": offset},
        )
        cols = list(result.keys())
        return [dict(zip(cols, row)) for row in result.fetchall()]


def _product_to_text(row: dict) -> str:
    return (
        "标题: " + str(row.get("title", "")) + "\n"
        "类目: " + str(row.get("category", "")) + "\n"
        "品牌: " + str(row.get("brand", "")) + "\n"
        "参数: " + str(row.get("specs", "")) + "\n"
        "价格: " + str(row.get("price", ""))
    )


def _review_to_text(row: dict) -> str:
    return "评价: " + str(row.get("review_text", ""))


def _product_to_milvus(row: dict, vec: list[float]) -> dict:
    return {
        "id": row["sku"],
        "vector": vec,
        "text": _product_to_text(row),
        "title": str(row.get("title", "")),
        "category": str(row.get("category", "")),
        "brand": str(row.get("brand", "")),
        "price": float(row.get("price", 0)),
    }


def _review_to_milvus(row: dict, vec: list[float]) -> dict:
    return {
        "id": str(row.get("review_id", "")),
        "vector": vec,
        "text": _review_to_text(row),
        "sku": str(row.get("sku", "")),
        "rating": float(row.get("rating", 0)),
        "review_date": str(row.get("review_date", "")),
    }


def _flush_to_milvus(collection_name: str, data: list[dict]) -> None:
    client = get_milvus_client()
    for attempt in range(3):
        try:
            client.upsert(collection_name=collection_name, data=data)
            return
        except Exception as e:
            if attempt < 2:
                logger.warning("Milvus write failed (retry %d): %s", attempt + 1, e)
                time.sleep(2 ** attempt)
            else:
                raise


def extract_chunk_node(state: BatchState) -> dict:
    chunk_index = state["chunk_index"]
    chunk_size = settings.CHUNK_SIZE
    offset = chunk_index * chunk_size

    cp = CheckpointManager(
        state["collection_name"], settings.OLLAMA_EMBED_MODEL, settings.OLLAMA_EMBED_DIM,
    )
    completed = cp.load_completed()
    if chunk_index in completed:
        logger.info("[Chunk %d/%d] already done, skipping", chunk_index + 1, state["total_chunks"])
        return {"skipped_count": state["skipped_count"] + 1, "rows": []}

    table = "products" if state["collection_name"] == "ecommerce_products" else "reviews"
    rows = _read_chunk(table, offset, chunk_size)
    logger.info("[Chunk %d/%d] read %d rows", chunk_index + 1, state["total_chunks"], len(rows))
    return {"rows": rows}


def embed_and_write_node(state: BatchState) -> dict:
    rows = state.get("rows", [])
    if not rows:
        return {}

    collection = state["collection_name"]
    is_products = collection == "ecommerce_products"
    to_text = _product_to_text if is_products else _review_to_text
    to_milvus = _product_to_milvus if is_products else _review_to_milvus

    buffer = []
    processed = 0
    failed = 0
    failed_ids = []

    for batch_start in tqdm(range(0, len(rows), settings.EMBED_BATCH_SIZE), desc="Embedding", ncols=100):
        batch = rows[batch_start:batch_start + settings.EMBED_BATCH_SIZE]
        texts = [to_text(r) for r in batch]

        try:
            vecs = embed_texts(texts)
        except Exception as e:
            logger.warning("Batch embed failed, falling back to single: %s", e)
            for row in batch:
                try:
                    v = embed_texts([to_text(row)])[0]
                    if validate_embedding(v):
                        buffer.append(to_milvus(row, v))
                    else:
                        failed += 1
                        failed_ids.append(str(row.get("sku", row.get("review_id", ""))))
                except Exception:
                    failed += 1
                    failed_ids.append(str(row.get("sku", row.get("review_id", ""))))
            continue

        for row, vec in zip(batch, vecs):
            if validate_embedding(vec):
                buffer.append(to_milvus(row, vec))
            else:
                failed += 1
                failed_ids.append(str(row.get("sku", row.get("review_id", ""))))

        if len(buffer) >= settings.MILVUS_INSERT_BATCH:
            _flush_to_milvus(collection, buffer)
            processed += len(buffer)
            buffer = []

    if buffer:
        _flush_to_milvus(collection, buffer)
        processed += len(buffer)

    cp = CheckpointManager(collection, settings.OLLAMA_EMBED_MODEL, settings.OLLAMA_EMBED_DIM)
    cp.mark_complete(state["chunk_index"])

    return {
        "processed_count": state["processed_count"] + processed,
        "failed_count": state["failed_count"] + failed,
        "failed_ids": state["failed_ids"] + failed_ids,
    }


def route_after_extract(state: BatchState) -> str:
    if not state.get("rows"):
        cp = CheckpointManager(
            state["collection_name"], settings.OLLAMA_EMBED_MODEL, settings.OLLAMA_EMBED_DIM,
        )
        completed = cp.load_completed()
        if state["chunk_index"] in completed:
            if state["chunk_index"] + 1 < state["total_chunks"]:
                return "skip_next"
            return "skip_done"
    return "process"


def route_next_node(state: BatchState) -> str:
    if state["chunk_index"] + 1 < state["total_chunks"]:
        return "next_chunk"
    return "done"


def advance_chunk_node(state: BatchState) -> dict:
    return {"chunk_index": state["chunk_index"] + 1, "rows": []}


def report_node(state: BatchState) -> dict:
    elapsed = time.time() - state["start_time"]
    client = get_milvus_client()
    client.load_collection(state["collection_name"])
    logger.info("=" * 60)
    logger.info("Batch Embedding Pipeline done (%s)", state["collection_name"])
    logger.info("  Processed:  %d", state["processed_count"])
    logger.info("  Skipped:    %d chunks", state.get("skipped_count", 0))
    logger.info("  Failed:     %d", state["failed_count"])
    logger.info("  Elapsed:    %.1fs", elapsed)
    if state["failed_ids"]:
        logger.warning("  Failed IDs (first 10): %s", state["failed_ids"][:10])
    logger.info("=" * 60)
    return {}


def build_pipeline() -> StateGraph:
    graph = StateGraph(BatchState)
    graph.add_node("extract", extract_chunk_node)
    graph.add_node("embed_write", embed_and_write_node)
    graph.add_node("advance", advance_chunk_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("extract")
    graph.add_conditional_edges("extract", route_after_extract, {
        "process": "embed_write",
        "skip_next": "advance",
        "skip_done": "report",
    })
    graph.add_edge("embed_write", "advance")
    graph.add_conditional_edges("advance", route_next_node, {
        "next_chunk": "extract",
        "done": "report",
    })
    graph.add_edge("report", END)

    return graph.compile()


def _run_pipeline(collection_name: str, table_name: str) -> None:
    total = _count_table(table_name)
    if total == 0:
        logger.warning("%s table is empty, run data generation first", table_name)
        return
    logger.info("Starting %s embedding: %d records", collection_name, total)
    pipeline = build_pipeline()
    pipeline.invoke({
        "collection_name": collection_name,
        "total_records": total,
        "chunk_index": 0,
        "total_chunks": math.ceil(total / settings.CHUNK_SIZE),
        "processed_count": 0,
        "skipped_count": 0,
        "failed_count": 0,
        "failed_ids": [],
        "start_time": time.time(),
        "rows": [],
    })


def run_products_embedding() -> None:
    create_products_collection()
    _run_pipeline("ecommerce_products", "products")


def run_reviews_embedding() -> None:
    create_reviews_collection()
    _run_pipeline("reviews_sku", "reviews")
