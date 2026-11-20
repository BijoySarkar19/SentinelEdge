import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.events import EdgeEventPayload
from app.schemas.incident import IncidentResponse, IncidentUpdate, StatusActionRequest
from app.services.incident import IncidentService

router = APIRouter()

@router.get("", response_model=dict)
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    camera_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)
    items, total = await service.get_incidents(skip, limit, severity, status_filter, camera_id)
    return {
        "items": [item.model_dump() for item in items],
        "total": total,
        "page": (skip // limit) + 1,
        "limit": limit,
    }

@router.post("/ingest", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_incident(
    event: EdgeEventPayload,
    db: AsyncSession = Depends(get_db),
):
    """Public edge ingestion endpoint for edge CV processor."""
    service = IncidentService(db)
    return await service.ingest_edge_event(event)

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)
    inc = await service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    update_in: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = IncidentService(db)
    if update_in.status:
        inc = await service.update_status(
            incident_id, update_in.status, user_id=current_user.id, comment=update_in.comment
        )
    else:
        inc = await service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("/{incident_id}/acknowledge", response_model=IncidentResponse)
async def acknowledge_incident(
    incident_id: uuid.UUID,
    action: StatusActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = IncidentService(db)
    inc = await service.update_status(
        incident_id, "acknowledged", user_id=current_user.id, comment=action.comment
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: uuid.UUID,
    action: StatusActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    service = IncidentService(db)
    inc = await service.update_status(
        incident_id, "resolved", user_id=current_user.id, comment=action.comment
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc
