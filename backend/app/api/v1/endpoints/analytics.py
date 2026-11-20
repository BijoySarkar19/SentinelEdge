from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics import SummaryMetric, TrendPoint, SeverityCount, CameraIncidentCount
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/summary", response_model=SummaryMetric)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_summary()

@router.get("/trends", response_model=list[TrendPoint])
async def get_trends(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_trends(days)

@router.get("/severity", response_model=list[SeverityCount])
async def get_severity_breakdown(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_severity_distribution()

@router.get("/cameras", response_model=list[CameraIncidentCount])
async def get_camera_breakdown(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_camera_activity()
