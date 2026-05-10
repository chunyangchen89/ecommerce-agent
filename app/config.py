from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_EMBED_MODEL: str = "bge-m3"
    OLLAMA_EMBED_DIM: int = 1024
    OLLAMA_LLM_MODEL: str = "qwen3:8b"

    # PostgreSQL
    POSTGRES_DSN: str = "postgresql+asyncpg://ecommerce:ecommerce@localhost:5432/ecommerce"

    # Milvus
    MILVUS_URI: str = "http://localhost:19530"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "http://localhost:3000"

    # Embedding pipeline
    EMBED_BATCH_SIZE: int = 32
    MILVUS_INSERT_BATCH: int = 500
    CHUNK_SIZE: int = 1000
    TOTAL_RECORDS: int = 10000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
