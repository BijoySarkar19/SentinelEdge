import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== BACKEND DB ====================

write("backend/app/db/base.py", '''
from datetime import datetime
from typing import Any
import uuid
from sqlalchemy import MetaData, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

POSTGRES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
''')

write("backend/app/db/session.py", '''
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.app_env == "development" and settings.log_level == "DEBUG",
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
''')

write("backend/app/db/init_db.py", '''
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User

logger = structlog.get_logger()

async def init_db(db: AsyncSession) -> None:
    """Bootstrap initial database state including default admin account."""
    if not settings.bootstrap_admin_username:
        return

    result = await db.execute(
        select(User).where(User.username == settings.bootstrap_admin_username)
    )
    user = result.scalar_one_or_none()

    if not user:
        password = settings.bootstrap_admin_password or "Admin@Sentinel2026!"
        admin = User(
            username=settings.bootstrap_admin_username,
            email=settings.bootstrap_admin_email or "admin@sentineledge.local",
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        logger.info(
            "Bootstrap admin created",
            username=admin.username,
            email=admin.email,
        )
    else:
        logger.info("Admin user already initialized", username=user.username)
''')

# ==================== BACKEND MODELS ====================

write("backend/app/models/user.py", '''
import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="operator", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    incident_audits = relationship("IncidentAudit", back_populates="user")
''')

write("backend/app/models/camera.py", '''
from typing import Optional
from sqlalchemy import String, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

class Camera(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cameras"

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(20), default="rtsp", nullable=False)  # rtsp, file, webcam, usb
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="offline", nullable=False)  # online, offline, processing, error
    processing_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    zones = relationship("Zone", back_populates="camera", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="camera", cascade="all, delete-orphan")
    rules = relationship("Rule", back_populates="camera", cascade="all, delete-orphan")
''')

write("backend/app/models/zone.py", '''
import uuid
from typing import Any
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

class Zone(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "zones"

    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    polygon_coordinates: Mapped[list[Any]] = mapped_column(JSON, nullable=False)  # list of [lat, lng] or [x, y]
    zone_type: Mapped[str] = mapped_column(String(30), default="restricted", nullable=False)  # crowd, restricted, vehicle, access_lane, custom

    camera = relationship("Camera", back_populates="zones")
    incidents = relationship("Incident", back_populates="zone")
    rules = relationship("Rule", back_populates="zone")
''')

write("backend/app/models/incident.py", '''
import uuid
from typing import Optional, Any
from sqlalchemy import String, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

class Incident(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incidents"

    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    rule_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False, index=True)  # informational, low, medium, high, critical
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)  # open, acknowledged, investigating, resolved, false_positive
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    object_counts: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    detected_classes: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    inference_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    camera = relationship("Camera", back_populates="incidents")
    zone = relationship("Zone", back_populates="incidents")
    audits = relationship("IncidentAudit", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentAudit.timestamp.desc()")
    embedding = relationship("IncidentEmbedding", back_populates="incident", uselist=False, cascade="all, delete-orphan")
''')

write("backend/app/models/incident_audit.py", '''
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin

class IncidentAudit(Base, UUIDMixin):
    __tablename__ = "incident_audits"

    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    incident = relationship("Incident", back_populates="audits")
    user = relationship("User", back_populates="incident_audits")
''')

write("backend/app/models/rule.py", '''
import uuid
from typing import Optional, Any
from sqlalchemy import String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

class Rule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rules"

    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # crowd_density, restricted_zone, vehicle_congestion, access_lane, custom
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    camera = relationship("Camera", back_populates="rules")
    zone = relationship("Zone", back_populates="rules")
''')

write("backend/app/models/detection_event.py", '''
import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDMixin

class DetectionEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "detection_events"

    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    object_counts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
''')

write("backend/app/models/incident_embedding.py", '''
import uuid
from typing import Any
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base, TimestampMixin, UUIDMixin

class IncidentEmbedding(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incident_embeddings"

    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), unique=True, nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(384), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), default="all-MiniLM-L6-v2", nullable=False)

    incident = relationship("Incident", back_populates="embedding")
''')

write("backend/app/models/audit_log.py", '''
import uuid
from typing import Optional, Any
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")
''')

write("backend/app/models/outbox_event.py", '''
from typing import Any, Optional
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDMixin

class OutboxEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "outbox_events"

    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
''')

write("backend/app/models/__init__.py", '''
from app.models.user import User
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.incident import Incident
from app.models.incident_audit import IncidentAudit
from app.models.rule import Rule
from app.models.detection_event import DetectionEvent
from app.models.incident_embedding import IncidentEmbedding
from app.models.audit_log import AuditLog
from app.models.outbox_event import OutboxEvent

__all__ = [
    "User",
    "Camera",
    "Zone",
    "Incident",
    "IncidentAudit",
    "Rule",
    "DetectionEvent",
    "IncidentEmbedding",
    "AuditLog",
    "OutboxEvent",
]
''')

print("Backend DB and Models generation complete.")
