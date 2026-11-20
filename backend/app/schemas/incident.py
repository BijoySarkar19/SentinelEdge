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
