import logging

from langfuse.decorators import langfuse_context

from app.config import settings

logger = logging.getLogger(__name__)

_initialized = False


def init_langfuse():
    global _initialized
    if _initialized:
        return
    if not is_langfuse_configured():
        return
    langfuse_context.configure(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
    )
    _initialized = True
    logger.info("Langfuse tracing enabled → %s", settings.LANGFUSE_HOST)


def is_langfuse_configured() -> bool:
    return bool(settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY)


def flush_langfuse():
    if _initialized:
        langfuse_context.flush()
