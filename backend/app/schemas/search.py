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
