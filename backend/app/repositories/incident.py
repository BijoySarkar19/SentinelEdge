import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import selectinload
from app.models.incident import Incident
from app.models.incident_audit import IncidentAudit
from app.models.camera import Camera

class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        camera_id: Optional[uuid.UUID] = None,
    ) -> tuple[Sequence[Incident], int]:
        filters = []
        if severity:
            filters.append(Incident.severity == severity)
        if status:
            filters.append(Incident.status == status)
        if camera_id:
            filters.append(Incident.camera_id == camera_id)

        count_stmt = select(func.count(Incident.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = (
            select(Incident)
            .options(selectinload(Incident.audits))
            .offset(skip)
            .limit(limit)
            .order_by(Incident.created_at.desc())
        )
        if filters:
            stmt = stmt.where(and_(*filters))

        res = await self.db.execute(stmt)
        return res.scalars().all(), total

    async def get_by_id(self, incident_id: uuid.UUID) -> Optional[Incident]:
        stmt = (
            select(Incident)
            .options(selectinload(Incident.audits))
            .where(Incident.id == incident_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_event_id(self, event_id: str) -> Optional[Incident]:
        stmt = (
            select(Incident)
            .options(selectinload(Incident.audits))
            .where(Incident.event_id == event_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        await self.db.commit()
        loaded = await self.get_by_id(incident.id)
        return loaded or incident

    async def update_status(
        self,
        incident_id: uuid.UUID,
        new_status: str,
        user_id: Optional[uuid.UUID] = None,
        comment: Optional[str] = None,
    ) -> Optional[Incident]:
        incident = await self.get_by_id(incident_id)
        if not incident:
            return None
        
        previous_status = incident.status
        incident.status = new_status
        
        audit = IncidentAudit(
            incident_id=incident.id,
            user_id=user_id,
            previous_status=previous_status,
            new_status=new_status,
            comment=comment,
        )
        self.db.add(audit)
        await self.db.commit()
        return await self.get_by_id(incident.id)
