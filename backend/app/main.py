import asyncio
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal
from app.db.init_db import init_db
from app.api.v1 import router as api_v1_router
from app.workers.event_consumer import run_redis_consumer
from app.workers.outbox_worker import run_outbox_publisher

setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SentinelEdge backend", env=settings.app_env)
    
    # Initialize DB bootstrap
    async with AsyncSessionLocal() as db:
        await init_db(db)

    # Launch background consumer & outbox tasks
    consumer_task = asyncio.create_task(run_redis_consumer())
    outbox_task = asyncio.create_task(run_outbox_publisher())

    yield

    logger.info("Shutting down SentinelEdge backend")
    consumer_task.cancel()
    outbox_task.cancel()
    await asyncio.gather(consumer_task, outbox_task, return_exceptions=True)

app = FastAPI(
    title="SentinelEdge API",
    description="Privacy-First Edge-to-Cloud Real-Time Video & Incident Intelligence Platform",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics Mount
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# API v1 Router
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "title": "SentinelEdge Incident Intelligence Platform",
        "tagline": "See the Risk. Protect the Privacy. Respond Intelligently.",
        "docs": "/api/docs",
        "api": "/api/v1",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sentineledge-backend"}
