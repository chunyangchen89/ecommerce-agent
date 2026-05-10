import logging

from app.data_generator.ddl import get_all_ddl
from app.db.milvus import get_milvus_client
from app.embedding.client import embed_texts, validate_embedding
from app.embedding.milvus_collections import create_table_metadata_collection
from app.models.dw_tables import Base

logger = logging.getLogger(__name__)


def _build_table_metadata() -> list[tuple[dict, str]]:
    """Build metadata from ORM + DDL. Returns list of (metadata_dict, ddl_text)."""
    ddls = get_all_ddl()
    results = []

    for table in Base.metadata.sorted_tables:
        description = table.comment or f"{table.name} table"
        key_columns = ", ".join(c.name for c in table.columns)
        example_queries = ", ".join(
            c.comment for c in table.columns if c.comment
        )
        ddl_text = ddls.get(table.name, "")

        entry = {
            "table_name": table.name,
            "description": description,
            "key_columns": key_columns,
            "example_queries": example_queries,
        }
        results.append((entry, ddl_text))

    return results


def embed_table_metadata() -> None:
    create_table_metadata_collection()
    client = get_milvus_client()

    table_metadata = _build_table_metadata()

    for entry, ddl_text in table_metadata:
        embed_text = (
            f"表名: {entry['table_name']}\n"
            f"描述: {entry['description']}\n"
            f"关键列: {entry['key_columns']}\n"
            f"示例查询: {entry['example_queries']}\n"
            f"DDL:\n{ddl_text}" if ddl_text else
            f"表名: {entry['table_name']}\n"
            f"描述: {entry['description']}\n"
            f"关键列: {entry['key_columns']}\n"
            f"示例查询: {entry['example_queries']}"
        )
        vecs = embed_texts([embed_text])
        if not vecs or not validate_embedding(vecs[0]):
            logger.error(f"Failed to embed table metadata for {entry['table_name']}")
            continue

        client.upsert(
            collection_name="table_metadata",
            data=[{
                "table_name": entry["table_name"],
                "vector": vecs[0],
                "text": embed_text,
                "description": entry["description"],
                "key_columns": entry["key_columns"],
                "example_queries": entry["example_queries"],
            }],
        )
        logger.info(f"Embedded table metadata: {entry['table_name']}")

    client.load_collection("table_metadata")
    logger.info(f"Table metadata embedding complete: {len(table_metadata)} tables")
