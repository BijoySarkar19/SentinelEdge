import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== SCHEMAS ====================

write("backend/app/schemas/auth.py", '''
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "operator"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
''')

write("backend/app/schemas/camera.py", '''
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    source_type: str = Field(default="rtsp", pattern="^(rtsp|file|webcam|usb)$")
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    processing_enabled: bool = True

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    source_type: Optional[str] = Field(None, pattern="^(rtsp|file|webcam|usb)$")
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    status: Optional[str] = Field(None, pattern="^(online|offline|processing|error)$")
    processing_enabled: Optional[bool] = None

class CameraResponse(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
''')

write("backend/app/schemas/events.py", '''
import uuid
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class EdgeEventPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(..., description="Unique event identifier")
    idempotency_key: str = Field(..., description="Unique key for deduplication")
    camera_id: str = Field(..., description="Camera identifier or UUID")
    zone_id: Optional[str] = None
    rule_id: Optional[str] = None
    
    event_type: str = Field(..., description="crowd_density, restricted_zone, vehicle_congestion, access_lane, custom")
    severity: str = Field(default="medium", pattern="^(informational|low|medium|high|critical)$")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    summary: str = Field(..., min_length=1)
    
    object_counts: dict[str, int] = Field(default_factory=dict)
    detected_classes: list[str] = Field(default_factory=list)
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    processing_device: str = Field(default="cpu")
    inference_backend: str = Field(default="yolo")
    inference_latency_ms: Optional[float] = Field(default=0.0)
    privacy_status: dict[str, Any] = Field(default_factory=lambda: {"mode": "metadata_only"})
    simulated: bool = Field(default=False)
''')

write("backend/app/schemas/incident.py", '''
import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class IncidentAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    previous_status: Optional[str] = None
    new_status: str
    comment: Optional[str] = None
    timestamp: datetime

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_id: str
    camera_id: uuid.UUID
    zone_id: Optional[uuid.UUID] = None
    rule_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    confidence: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    object_counts: Optional[dict[str, Any]] = None
    detected_classes: Optional[list[str]] = None
    inference_latency_ms: Optional[float] = None
    simulated: bool
    created_at: datetime
    updated_at: datetime
    audits: list[IncidentAuditResponse] = []

class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(open|acknowledged|investigating|resolved|false_positive)$")
    description: Optional[str] = None
    comment: Optional[str] = None

class StatusActionRequest(BaseModel):
    comment: Optional[str] = None
''')

write("backend/app/schemas/rule.py", '''
import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class RuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    camera_id: uuid.UUID
    zone_id: Optional[uuid.UUID] = None
    rule_type: str = Field(..., description="crowd_density, restricted_zone, vehicle_congestion, access_lane, custom")
    configuration: dict[str, Any] = Field(default_factory=dict)
    severity: str = Field(default="medium", pattern="^(informational|low|medium|high|critical)$")
    is_enabled: bool = True

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    zone_id: Optional[uuid.UUID] = None
    configuration: Optional[dict[str, Any]] = None
    severity: Optional[str] = Field(None, pattern="^(informational|low|medium|high|critical)$")
    is_enabled: Optional[bool] = None

class RuleResponse(RuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
''')

write("backend/app/schemas/analytics.py", '''
from typing import Optional
from pydantic import BaseModel

class SummaryMetric(BaseModel):
    total_cameras: int
    active_cameras: int
    total_incidents: int
    open_incidents: int
    critical_incidents: int
    resolved_incidents: int
    avg_inference_latency_ms: float
    event_volume_24h: int

class TrendPoint(BaseModel):
    date: str
    count: int
    critical_count: int

class SeverityCount(BaseModel):
    severity: str
    count: int

class CameraIncidentCount(BaseModel):
    camera_id: str
    camera_name: str
    incident_count: int
''')

write("backend/app/schemas/search.py", '''
from typing import Optional
from pydantic import BaseModel, Field

class SemanticSearchQuery(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language search query")
    limit: int = Field(default=10, ge=1, le=100)
    severity: Optional[str] = None
    camera_id: Optional[str] = None
    status: Optional[str] = None

class SemanticSearchResultItem(BaseModel):
    incident_id: str
    title: str
    description: Optional[str]
    severity: str
    status: str
    confidence: float
    similarity_score: float
    camera_id: str
    created_at: str

class SemanticSearchResponse(BaseModel):
    query: str
    total: int
    search_latency_ms: float
    results: list[SemanticSearchResultItem]
''')

write("backend/app/schemas/health.py", '''
from typing import Optional, Any
from pydantic import BaseModel

class ComponentHealth(BaseModel):
    status: str
    latency_ms: Optional[float] = None
    message: Optional[str] = None

class SystemHealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
    components: dict[str, ComponentHealth] = {}
''')

write("backend/app/schemas/__init__.py", '''
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.schemas.events import EdgeEventPayload
from app.schemas.incident import IncidentResponse, IncidentUpdate, IncidentAuditResponse, StatusActionRequest
from app.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from app.schemas.analytics import SummaryMetric, TrendPoint, SeverityCount, CameraIncidentCount
from app.schemas.search import SemanticSearchQuery, SemanticSearchResponse
from app.schemas.health import SystemHealthResponse, ComponentHealth

__all__ = [
    "LoginRequest", "TokenResponse", "UserCreate", "UserResponse",
    "CameraCreate", "CameraUpdate", "CameraResponse",
    "EdgeEventPayload", "IncidentResponse", "IncidentUpdate", "IncidentAuditResponse", "StatusActionRequest",
    "RuleCreate", "RuleUpdate", "RuleResponse",
    "SummaryMetric", "TrendPoint", "SeverityCount", "CameraIncidentCount",
    "SemanticSearchQuery", "SemanticSearchResponse",
    "SystemHealthResponse", "ComponentHealth",
]
''')

# ==================== REPOSITORIES ====================

write("backend/app/repositories/user.py", '''
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
''')

write("backend/app/repositories/camera.py", '''
import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate

class CameraRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Camera]:
        result = await self.db.execute(select(Camera).offset(skip).limit(limit).order_by(Camera.created_at.desc()))
        return result.scalars().all()

    async def get_by_id(self, camera_id: uuid.UUID) -> Optional[Camera]:
        result = await self.db.execute(select(Camera).where(Camera.id == camera_id))
        return result.scalar_one_or_none()

    async def create(self, camera_in: CameraCreate) -> Camera:
        camera = Camera(**camera_in.model_dump())
        self.db.add(camera)
        await self.db.commit()
        await self.db.refresh(camera)
        return camera

    async def update(self, camera_id: uuid.UUID, camera_in: CameraUpdate) -> Optional[Camera]:
        camera = await self.get_by_id(camera_id)
        if not camera:
            return None
        update_data = camera_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(camera, key, val)
        await self.db.commit()
        await self.db.refresh(camera)
        return camera

    async def delete(self, camera_id: uuid.UUID) -> bool:
        camera = await self.get_by_id(camera_id)
        if not camera:
            return False
        await self.db.delete(camera)
        await self.db.commit()
        return True
''')

write("backend/app/repositories/incident.py", '''
import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import selectinload
from app.models.incident import Incident
from app.models.incident_audit import IncidentAudit
from app.models.camera import Camera

class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        camera_id: Optional[uuid.UUID] = None,
    ) -> tuple[Sequence[Incident], int]:
        filters = []
        if severity:
            filters.append(Incident.severity == severity)
        if status:
            filters.append(Incident.status == status)
        if camera_id:
            filters.append(Incident.camera_id == camera_id)

        count_stmt = select(func.count(Incident.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = (
            select(Incident)
            .options(selectinload(Incident.audits))
            .offset(skip)
            .limit(limit)
            .order_by(Incident.created_at.desc())
        )
        if filters:
            stmt = stmt.where(and_(*filters))

        res = await self.db.execute(stmt)
        return res.scalars().all(), total

    async def get_by_id(self, incident_id: uuid.UUID) -> Optional[Incident]:
        stmt = (
            select(Incident)
            .options(selectinload(Incident.audits))
            .where(Incident.id == incident_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_event_id(self, event_id: str) -> Optional[Incident]:
        stmt = (
            select(Incident)
            .options(selectinload(Incident.audits))
            .where(Incident.event_id == event_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def update_status(
        self,
        incident_id: uuid.UUID,
        new_status: str,
        user_id: Optional[uuid.UUID] = None,
        comment: Optional[str] = None,
    ) -> Optional[Incident]:
        incident = await self.get_by_id(incident_id)
        if not incident:
            return None
        
        previous_status = incident.status
        incident.status = new_status
        
        audit = IncidentAudit(
            incident_id=incident.id,
            user_id=user_id,
            previous_status=previous_status,
            new_status=new_status,
            comment=comment,
        )
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(incident)
        return incident
''')

write("backend/app/repositories/__init__.py", '''
from app.repositories.user import UserRepository
from app.repositories.camera import CameraRepository
from app.repositories.incident import IncidentRepository

__all__ = ["UserRepository", "CameraRepository", "IncidentRepository"]
''')

# ==================== BROKERS ====================

write("backend/app/brokers/base.py", '''
from abc import ABC, abstractmethod
from typing import Any, Optional

class EventBroker(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def publish(self, topic: str, key: str, payload: dict[str, Any]) -> str:
        pass
''')

write("backend/app/brokers/redis_broker.py", '''
import json
import structlog
from typing import Any
import redis.asyncio as aioredis
from app.brokers.base import EventBroker
from app.core.config import settings

logger = structlog.get_logger()

class RedisStreamsBroker(EventBroker):
    def __init__(self, url: str):
        self.url = url
        self.redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        if not self.redis:
            self.redis = aioredis.from_url(self.url, decode_responses=True)
            logger.info("Connected to Redis Streams", url=self.url)

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def publish(self, topic: str, key: str, payload: dict[str, Any]) -> str:
        await self.connect()
        data = {
            "key": key,
            "payload": json.dumps(payload),
        }
        msg_id = await self.redis.xadd(topic, data)
        return str(msg_id)

    async def ensure_consumer_group(self, topic: str, group: str) -> None:
        await self.connect()
        try:
            await self.redis.xgroup_create(topic, group, id="0", mkstream=True)
            logger.info("Created consumer group", group=group, topic=topic)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                logger.warning("Error creating consumer group", error=str(e))
''')

write("backend/app/brokers/kafka_broker.py", '''
import json
import structlog
from typing import Any
from app.brokers.base import EventBroker

logger = structlog.get_logger()

class KafkaBroker(EventBroker):
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def connect(self) -> None:
        try:
            from aiokafka import AIOKafkaProducer
            if not self.producer:
                self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
                await self.producer.start()
                logger.info("Connected to Redpanda/Kafka", servers=self.bootstrap_servers)
        except ImportError:
            logger.warning("aiokafka not installed; falling back to stub mode")

    async def disconnect(self) -> None:
        if self.producer:
            await self.producer.stop()
            self.producer = None

    async def publish(self, topic: str, key: str, payload: dict[str, Any]) -> str:
        await self.connect()
        if self.producer:
            encoded_val = json.dumps(payload).encode("utf-8")
            encoded_key = key.encode("utf-8")
            record = await self.producer.send_and_wait(topic, key=encoded_key, value=encoded_val)
            return f"{record.offset}"
        logger.info("[Kafka Stub] Published", topic=topic, key=key)
        return "stub-offset"
''')

write("backend/app/brokers/factory.py", '''
from app.core.config import settings
from app.brokers.base import EventBroker
from app.brokers.redis_broker import RedisStreamsBroker
from app.brokers.kafka_broker import KafkaBroker

_broker_instance: EventBroker | None = None

def get_event_broker() -> EventBroker:
    global _broker_instance
    if _broker_instance is None:
        if settings.event_broker == "kafka":
            _broker_instance = KafkaBroker(settings.kafka_bootstrap_servers)
        else:
            _broker_instance = RedisStreamsBroker(settings.redis_url)
    return _broker_instance
''')

write("backend/app/brokers/__init__.py", '''
from app.brokers.base import EventBroker
from app.brokers.redis_broker import RedisStreamsBroker
from app.brokers.kafka_broker import KafkaBroker
from app.brokers.factory import get_event_broker

__all__ = ["EventBroker", "RedisStreamsBroker", "KafkaBroker", "get_event_broker"]
''')

# ==================== WEBSOCKET MANAGER ====================

write("backend/app/websocket/manager.py", '''
import json
import structlog
from typing import Any
from fastapi import WebSocket

logger = structlog.get_logger()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug("WebSocket client connected", count=len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.debug("WebSocket client disconnected", count=len(self.active_connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_connections.append(connection)
        for dc in dead_connections:
            self.disconnect(dc)

manager = ConnectionManager()
''')

write("backend/app/websocket/__init__.py", '''
from app.websocket.manager import ConnectionManager, manager

__all__ = ["ConnectionManager", "manager"]
''')

# ==================== MONITORING ====================

write("backend/app/monitoring/metrics.py", '''
from prometheus_client import Counter, Histogram, Gauge

# Computer vision edge metrics
EDGE_FRAMES_PROCESSED = Counter(
    "sentinel_edge_frames_total",
    "Total video frames processed by edge runtime",
    ["camera_id", "device"]
)

EDGE_INFERENCE_LATENCY = Histogram(
    "sentinel_edge_inference_latency_seconds",
    "Inference execution time in seconds",
    ["model", "device"],
    buckets=[0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0]
)

EDGE_PRIVACY_FILTER_LATENCY = Histogram(
    "sentinel_edge_privacy_filter_latency_seconds",
    "Time taken to detect and anonymize faces/plates",
    buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
)

# Backend ingestion metrics
INGESTED_EVENTS_TOTAL = Counter(
    "sentinel_ingested_events_total",
    "Total detection and incident events ingested",
    ["event_type", "severity", "simulated"]
)

ACTIVE_WEBSOCKET_CONNECTIONS = Gauge(
    "sentinel_active_websocket_connections",
    "Number of active WebSocket connections to the incident feed"
)

# Semantic search metrics
SEARCH_LATENCY = Histogram(
    "sentinel_semantic_search_latency_seconds",
    "Search execution latency for semantic pgvector retrieval",
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
)
''')

write("backend/app/monitoring/__init__.py", '''
from app.monitoring.metrics import (
    EDGE_FRAMES_PROCESSED,
    EDGE_INFERENCE_LATENCY,
    EDGE_PRIVACY_FILTER_LATENCY,
    INGESTED_EVENTS_TOTAL,
    ACTIVE_WEBSOCKET_CONNECTIONS,
    SEARCH_LATENCY,
)

__all__ = [
    "EDGE_FRAMES_PROCESSED",
    "EDGE_INFERENCE_LATENCY",
    "EDGE_PRIVACY_FILTER_LATENCY",
    "INGESTED_EVENTS_TOTAL",
    "ACTIVE_WEBSOCKET_CONNECTIONS",
    "SEARCH_LATENCY",
]
''')

print("Backend Part 2 generation complete.")
