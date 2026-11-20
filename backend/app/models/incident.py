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

    camera = relationship("Camera", back_populates="incidents", lazy="selectin")
    zone = relationship("Zone", back_populates="incidents", lazy="selectin")
    audits = relationship("IncidentAudit", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentAudit.timestamp.desc()", lazy="selectin")
    embedding = relationship("IncidentEmbedding", back_populates="incident", uselist=False, cascade="all, delete-orphan", lazy="selectin")
