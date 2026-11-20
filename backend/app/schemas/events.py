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
