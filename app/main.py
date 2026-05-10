import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db.langfuse import flush_langfuse, init_langfuse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting Ecommerce Data Agent API")
    init_langfuse()
    yield
    flush_langfuse()
    logging.info("Shutting down")


app = FastAPI(title="Ecommerce Data Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
