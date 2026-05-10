import logging

from pymilvus import CollectionSchema, DataType, FieldSchema

from app.config import settings
from app.db.milvus import get_milvus_client

logger = logging.getLogger(__name__)

# Vector index: HNSW (explicit params for recall/latency control; default is AUTOINDEX)
# Scalar index: INVERTED (default scalar index type, works for all field types)


def create_table_metadata_collection() -> None:
    client = get_milvus_client()
    name = "table_metadata"
    if client.has_collection(name):
        logger.info(f"Collection '{name}' already exists")
        return
    schema = CollectionSchema(fields=[
        FieldSchema("table_name", DataType.VARCHAR, is_primary=True, max_length=64, description="表名"),
        FieldSchema("vector", DataType.FLOAT_VECTOR, dim=settings.OLLAMA_EMBED_DIM, description="Schema embedding"),
        FieldSchema("text", DataType.VARCHAR, max_length=4096, description="Schema描述文本"),
        FieldSchema("description", DataType.VARCHAR, max_length=1024, description="表描述"),
        FieldSchema("key_columns", DataType.VARCHAR, max_length=512, description="关键列"),
        FieldSchema("example_queries", DataType.VARCHAR, max_length=512, description="示例查询"),
    ])
    client.create_collection(collection_name=name, schema=schema)
    client.create_index(
        collection_name=name,
        index_params=client.prepare_index_params(
            field_name="vector",
            index_type="HNSW",
            metric_type="COSINE",
            params={"M": 16, "efConstruction": 256},
        ),
    )
    logger.info(f"Collection '{name}' created")


def create_products_collection() -> None:
    client = get_milvus_client()
    name = "ecommerce_products"
    if client.has_collection(name):
        logger.info(f"Collection '{name}' already exists")
        return
    schema = CollectionSchema(fields=[
        FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=64, description="SKU"),
        FieldSchema("vector", DataType.FLOAT_VECTOR, dim=settings.OLLAMA_EMBED_DIM, description="商品embedding"),
        FieldSchema("text", DataType.VARCHAR, max_length=4096, description="组合文本"),
        FieldSchema("title", DataType.VARCHAR, max_length=512, description="商品标题"),
        FieldSchema("category", DataType.VARCHAR, max_length=64, description="类目"),
        FieldSchema("brand", DataType.VARCHAR, max_length=64, description="品牌"),
        FieldSchema("price", DataType.FLOAT, description="价格"),
    ])
    client.create_collection(collection_name=name, schema=schema)
    client.create_index(
        collection_name=name,
        index_params=client.prepare_index_params(
            field_name="vector",
            index_type="HNSW",
            metric_type="COSINE",
            params={"M": 16, "efConstruction": 256},
        ),
    )
    for field in ["category", "brand"]:
        client.create_index(
            collection_name=name,
            index_params=client.prepare_index_params(
                field_name=field,
                index_type="INVERTED",
            ),
        )
    logger.info(f"Collection '{name}' created")


def create_reviews_collection() -> None:
    client = get_milvus_client()
    name = "reviews_sku"
    if client.has_collection(name):
        logger.info(f"Collection '{name}' already exists")
        return
    schema = CollectionSchema(fields=[
        FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=64, description="review_id"),
        FieldSchema("vector", DataType.FLOAT_VECTOR, dim=settings.OLLAMA_EMBED_DIM, description="评价embedding"),
        FieldSchema("text", DataType.VARCHAR, max_length=4096, description="评价原文"),
        FieldSchema("sku", DataType.VARCHAR, max_length=64, description="商品SKU"),
        FieldSchema("rating", DataType.FLOAT, description="评分"),
        FieldSchema("review_date", DataType.VARCHAR, max_length=32, description="评价日期"),
    ])
    client.create_collection(collection_name=name, schema=schema)
    client.create_index(
        collection_name=name,
        index_params=client.prepare_index_params(
            field_name="vector",
            index_type="HNSW",
            metric_type="COSINE",
            params={"M": 16, "efConstruction": 256},
        ),
    )
    for field in ["sku", "rating"]:
        client.create_index(
            collection_name=name,
            index_params=client.prepare_index_params(
                field_name=field,
                index_type="INVERTED",
            ),
        )
    logger.info(f"Collection '{name}' created")


def create_all_collections() -> None:
    create_table_metadata_collection()
    create_products_collection()
    create_reviews_collection()
