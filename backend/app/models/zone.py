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
