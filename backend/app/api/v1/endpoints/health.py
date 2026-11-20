import time
import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
from app.schemas.health import SystemHealthResponse, ComponentHealth
import redis.asyncio as aioredis

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=dict)
async def liveness():
    return {"status": "ok", "app": "SentinelEdge", "version": "0.1.0"}

@router.get("/ready", response_model=SystemHealthResponse)
async def readiness(db: AsyncSession = Depends(get_db)):
    components = {}
    overall = "healthy"

    # DB check
    t0 = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        db_lat = (time.perf_counter() - t0) * 1000.0
        components["postgres"] = ComponentHealth(status="healthy", latency_ms=round(db_lat, 2))
    except Exception as e:
        components["postgres"] = ComponentHealth(status="unhealthy", message=str(e))
        overall = "degraded"

    # Redis check
    t0 = time.perf_counter()
    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        r_lat = (time.perf_counter() - t0) * 1000.0
        components["redis"] = ComponentHealth(status="healthy", latency_ms=round(r_lat, 2))
    except Exception as e:
        components["redis"] = ComponentHealth(status="unhealthy", message=str(e))
        overall = "degraded"

    components["event_broker"] = ComponentHealth(status="healthy", message=f"Configured: {settings.event_broker}")
    components["ai_model"] = ComponentHealth(status="healthy", message=f"Model: {settings.embedding_model}")

    return SystemHealthResponse(status=overall, version="0.1.0", components=components)

@router.get("/metrics")
async def system_metrics():
    return {
        "system": {
            "version": "0.1.0",
            "env": settings.app_env,
            "broker": settings.event_broker,
            "inference_device": settings.inference_device,
        }
    }
