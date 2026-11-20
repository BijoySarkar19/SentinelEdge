from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.search import SemanticSearchQuery, SemanticSearchResponse
from app.search.embedder import search_incidents

router = APIRouter()

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    body: SemanticSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await search_incidents(
        db=db,
        query=body.query,
        limit=body.limit,
        severity=body.severity,
        camera_id=body.camera_id,
        status=body.status,
    )

@router.get("/history")
async def search_history(current_user: User = Depends(get_current_user)):
    return {
        "recent_queries": [
            "Crowd density at gate 2",
            "Vehicle congestion on highway access",
            "High severity incidents last week",
            "Blocked emergency lane",
            "Restricted area nighttime activity",
        ]
    }
