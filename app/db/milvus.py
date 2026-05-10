from pymilvus import MilvusClient

from app.config import settings

_client: MilvusClient | None = None


def get_milvus_client() -> MilvusClient:
    global _client
    if _client is None:
        _client = MilvusClient(uri=settings.MILVUS_URI)
    return _client
