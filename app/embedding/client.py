import logging
import math
import time

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def get_embed_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key="ollama")
    return _client


def validate_embedding(vec: list[float], dim: int | None = None) -> bool:
    dim = dim or settings.OLLAMA_EMBED_DIM
    if len(vec) != dim:
        logger.warning(f"向量维度错误: 期望 {dim}, 实际 {len(vec)}")
        return False
    if all(v == 0.0 for v in vec):
        logger.warning("向量为全零 (模型推理可能失败)")
        return False
    norm = math.sqrt(sum(v * v for v in vec))
    if norm < 0.1 or norm > 10.0:
        logger.warning(f"向量 L2 范数异常: {norm:.4f}")
        return False
    return True


def embed_texts(texts: list[str], max_retries: int = 3) -> list[list[float]]:
    client = get_embed_client()
    for attempt in range(max_retries):
        try:
            resp = client.embeddings.create(
                model=settings.OLLAMA_EMBED_MODEL,
                input=texts,
                dimensions=settings.OLLAMA_EMBED_DIM,
            )
            return [item.embedding for item in resp.data]
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning(f"批量 Embedding 失败 (重试 {attempt + 1}/{max_retries}): {e}, 等待 {wait}s")
                time.sleep(wait)
            else:
                raise
    return []
