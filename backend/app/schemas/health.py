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
