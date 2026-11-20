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
