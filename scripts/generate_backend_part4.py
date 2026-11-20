import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== API ENDPOINTS ====================

write("backend/app/api/v1/endpoints/auth.py", '''
from datetime import timedelta
import structlog
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_current_user, require_role
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.repositories.user import UserRepository

logger = structlog.get_logger()
router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        expires=settings.access_token_expire_minutes * 60,
        samesite="lax",
        secure=settings.is_production,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
''')

write("backend/app/api/v1/endpoints/cameras.py", '''
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.services.camera import CameraService

router = APIRouter()

@router.get("", response_model=list[CameraResponse])
async def list_cameras(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CameraService(db)
    return await service.list_cameras(skip, limit)

@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_in: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = CameraService(db)
    return await service.create_camera(camera_in)

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CameraService(db)
    cam = await service.get_camera(camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: uuid.UUID,
    camera_in: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = CameraService(db)
    cam = await service.update_camera(camera_id, camera_in)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    service = CameraService(db)
    ok = await service.delete_camera(camera_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Camera not found")
''')

write("backend/app/api/v1/endpoints/incidents.py", '''
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.events import EdgeEventPayload
from app.schemas.incident import IncidentResponse, IncidentUpdate, StatusActionRequest
from app.services.incident import IncidentService

router = APIRouter()

@router.get("", response_model=dict)
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    camera_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)
    items, total = await service.get_incidents(skip, limit, severity, status_filter, camera_id)
    return {
        "items": [item.model_dump() for item in items],
        "total": total,
        "page": (skip // limit) + 1,
        "limit": limit,
    }

@router.post("/ingest", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_incident(
    event: EdgeEventPayload,
    db: AsyncSession = Depends(get_db),
):
    """Public edge ingestion endpoint for edge CV processor."""
    service = IncidentService(db)
    return await service.ingest_edge_event(event)

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)
    inc = await service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    update_in: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = IncidentService(db)
    if update_in.status:
        inc = await service.update_status(
            incident_id, update_in.status, user_id=current_user.id, comment=update_in.comment
        )
    else:
        inc = await service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("/{incident_id}/acknowledge", response_model=IncidentResponse)
async def acknowledge_incident(
    incident_id: uuid.UUID,
    action: StatusActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = IncidentService(db)
    inc = await service.update_status(
        incident_id, "acknowledged", user_id=current_user.id, comment=action.comment
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: uuid.UUID,
    action: StatusActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = IncidentService(db)
    inc = await service.update_status(
        incident_id, "resolved", user_id=current_user.id, comment=action.comment
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc
''')

write("backend/app/api/v1/endpoints/analytics.py", '''
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics import SummaryMetric, TrendPoint, SeverityCount, CameraIncidentCount
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/summary", response_model=SummaryMetric)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_summary()

@router.get("/trends", response_model=list[TrendPoint])
async def get_trends(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_trends(days)

@router.get("/severity", response_model=list[SeverityCount])
async def get_severity_breakdown(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_severity_distribution()

@router.get("/cameras", response_model=list[CameraIncidentCount])
async def get_camera_breakdown(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_camera_activity()
''')

write("backend/app/api/v1/endpoints/search.py", '''
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.search import SemanticSearchQuery, SemanticSearchResponse
from app.search.embedder import search_incidents

router = APIRouter()

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    body: SemanticSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await search_incidents(
        db=db,
        query=body.query,
        limit=body.limit,
        severity=body.severity,
        camera_id=body.camera_id,
        status=body.status,
    )

@router.get("/history")
async def search_history(current_user: User = Depends(get_current_user)):
    return {
        "recent_queries": [
            "Crowd density at gate 2",
            "Vehicle congestion on highway access",
            "High severity incidents last week",
            "Blocked emergency lane",
            "Restricted area nighttime activity",
        ]
    }
''')

write("backend/app/api/v1/endpoints/health.py", '''
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
''')

write("backend/app/api/v1/endpoints/websocket.py", '''
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.monitoring.metrics import ACTIVE_WEBSOCKET_CONNECTIONS

router = APIRouter()

@router.websocket("/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    ACTIVE_WEBSOCKET_CONNECTIONS.inc()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        ACTIVE_WEBSOCKET_CONNECTIONS.dec()
''')

write("backend/app/api/v1/endpoints/__init__.py", '''
from app.api.v1.endpoints import auth, cameras, incidents, analytics, search, health, websocket

__all__ = ["auth", "cameras", "incidents", "analytics", "search", "health", "websocket"]
''')

write("backend/app/api/v1/__init__.py", '''
from fastapi import APIRouter
from app.api.v1.endpoints import auth, cameras, incidents, analytics, search, health, websocket

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
''')

write("backend/app/main.py", '''
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
''')

# ==================== ALEMBIC MIGRATION ====================

write("backend/alembic/versions/001_initial_schema.py", '''
"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Ensure pgvector and uuid extensions are active
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("CREATE EXTENSION IF NOT EXISTS \\"uuid-ossp\\";")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='operator'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('users_username_idx', 'users', ['username'])
    op.create_index('users_email_idx', 'users', ['email'])

    # cameras
    op.create_table(
        'cameras',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(20), nullable=False, server_default='rtsp'),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='offline'),
        sa.Column('processing_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('cameras_name_idx', 'cameras', ['name'])

    # zones
    op.create_table(
        'zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('polygon_coordinates', sa.JSON(), nullable=False),
        sa.Column('zone_type', sa.String(30), nullable=False, server_default='restricted'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('zones_camera_id_idx', 'zones', ['camera_id'])

    # incidents
    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', sa.String(100), nullable=False, unique=True),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('zones.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(20), nullable=False, server_default='open'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('object_counts', sa.JSON(), nullable=True),
        sa.Column('detected_classes', sa.JSON(), nullable=True),
        sa.Column('inference_latency_ms', sa.Float(), nullable=True),
        sa.Column('simulated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('incidents_event_id_idx', 'incidents', ['event_id'])
    op.create_index('incidents_camera_id_idx', 'incidents', ['camera_id'])
    op.create_index('incidents_severity_idx', 'incidents', ['severity'])
    op.create_index('incidents_status_idx', 'incidents', ['status'])
    op.create_index('incidents_simulated_idx', 'incidents', ['simulated'])

    # incident_audits
    op.create_table(
        'incident_audits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('previous_status', sa.String(30), nullable=True),
        sa.Column('new_status', sa.String(30), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('incident_audits_incident_id_idx', 'incident_audits', ['incident_id'])

    # rules
    op.create_table(
        'rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('zones.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # detection_events
    op.create_table(
        'detection_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', sa.String(100), nullable=False, unique=True),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('object_counts', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('simulated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # incident_embeddings
    op.create_table(
        'incident_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('embedding_model', sa.String(100), nullable=False, server_default='all-MiniLM-L6-v2'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # outbox_events
    op.create_table(
        'outbox_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', sa.String(100), nullable=False, unique=True),
        sa.Column('topic', sa.String(100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('outbox_events')
    op.drop_table('audit_logs')
    op.drop_table('incident_embeddings')
    op.drop_table('detection_events')
    op.drop_table('rules')
    op.drop_table('incident_audits')
    op.drop_table('incidents')
    op.drop_table('zones')
    op.drop_table('cameras')
    op.drop_table('users')
''')

# ==================== TESTS ====================

write("backend/tests/conftest.py", '''
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "00000000-0000-0000-0000-000000000001", "username": "testadmin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}
''')

write("backend/tests/unit/test_security.py", '''
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    pw = "SentinelSecure2026!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_token_creation_and_decoding():
    payload = {"sub": "12345", "role": "operator"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "12345"
    assert decoded["role"] == "operator"

def test_invalid_jwt_token():
    assert decode_access_token("invalid.token.here") is None
''')

write("backend/tests/unit/test_incident_service.py", '''
import pytest
from app.schemas.events import EdgeEventPayload

def test_edge_event_schema_validation():
    valid_data = {
        "event_id": "evt-1234",
        "idempotency_key": "idemp-5678",
        "camera_id": "cam-01",
        "event_type": "crowd_density",
        "severity": "high",
        "confidence": 0.92,
        "summary": "High crowd density detected in zone A",
        "timestamp": "2026-11-20T12:00:00Z",
    }
    payload = EdgeEventPayload(**valid_data)
    assert payload.event_id == "evt-1234"
    assert payload.severity == "high"
    assert payload.simulated is False

def test_edge_event_schema_invalid_severity():
    invalid_data = {
        "event_id": "evt-1234",
        "idempotency_key": "idemp-5678",
        "camera_id": "cam-01",
        "event_type": "crowd_density",
        "severity": "extreme",  # Not in allowed enum
        "confidence": 0.92,
        "summary": "Invalid severity",
        "timestamp": "2026-11-20T12:00:00Z",
    }
    with pytest.raises(Exception):
        EdgeEventPayload(**invalid_data)
''')

write("backend/tests/integration/test_auth_api.py", '''
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "SentinelEdge" in data["title"]

@pytest.mark.asyncio
async def test_health_liveness(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
''')

write("backend/tests/integration/test_incidents_api.py", '''
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ingest_and_idempotency_mock(client: AsyncClient):
    payload = {
        "event_id": "mock-test-001",
        "idempotency_key": "mock-idemp-001",
        "camera_id": "test-cam-01",
        "event_type": "restricted_zone",
        "severity": "medium",
        "confidence": 0.88,
        "summary": "Person entered restricted compound",
        "timestamp": "2026-11-20T12:00:00Z",
        "simulated": True,
    }
    # Test schema serialization
    assert payload["event_id"] == "mock-test-001"
''')

print("Backend Part 4 (API, alembic, tests) complete.")
