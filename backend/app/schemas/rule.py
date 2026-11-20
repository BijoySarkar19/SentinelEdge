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
