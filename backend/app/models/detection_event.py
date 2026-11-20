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
