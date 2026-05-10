import logging
import time

import redis as redis_lib

from app.config import settings

logger = logging.getLogger(__name__)

_redis = None


def _get_redis():
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


class CheckpointManager:
    def __init__(self, collection: str, model: str, dim: int):
        self.collection = collection
        self.model = model
        self.dim = dim
        self.cp_key = f"emb_cp:{collection}:{model}"
        self.meta_key = f"{self.cp_key}:meta"

    def _check_model_version(self) -> bool:
        r = _get_redis()
        saved_model = r.hget(self.meta_key, "model")
        saved_dim = r.hget(self.meta_key, "dim")
        if saved_model and (saved_model != self.model or int(saved_dim) != self.dim):
            logger.warning(f"模型变更: {saved_model}/{saved_dim} → {self.model}/{self.dim}, 清除旧 checkpoint")
            r.delete(self.cp_key, self.meta_key)
            return True
        return False

    def load_completed(self) -> set[int]:
        self._check_model_version()
        completed = _get_redis().smembers(self.cp_key)
        result = {int(x) for x in completed}
        if result:
            logger.info(f"加载 checkpoint: 已完成 {len(result)} 个 chunk")
        return result

    def mark_complete(self, chunk_index: int) -> None:
        r = _get_redis()
        pipe = r.pipeline()
        pipe.sadd(self.cp_key, chunk_index)
        pipe.hset(self.meta_key, mapping={
            "model": self.model,
            "dim": str(self.dim),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        pipe.execute()
