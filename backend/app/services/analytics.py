from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from datetime import datetime, timedelta, timezone
from app.models.camera import Camera
from app.models.incident import Incident
from app.schemas.analytics import SummaryMetric, TrendPoint, SeverityCount, CameraIncidentCount

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self) -> SummaryMetric:
        # Cameras
        cams_res = await self.db.execute(select(func.count(Camera.id)))
        total_cameras = cams_res.scalar() or 0

        active_res = await self.db.execute(
            select(func.count(Camera.id)).where(Camera.status.in_(["online", "processing"]))
        )
        active_cameras = active_res.scalar() or 0

        # Incidents
        inc_res = await self.db.execute(select(func.count(Incident.id)))
        total_incidents = inc_res.scalar() or 0

        open_res = await self.db.execute(
            select(func.count(Incident.id)).where(Incident.status == "open")
        )
        open_incidents = open_res.scalar() or 0

        crit_res = await self.db.execute(
            select(func.count(Incident.id)).where(Incident.severity == "critical")
        )
        critical_incidents = crit_res.scalar() or 0

        res_res = await self.db.execute(
            select(func.count(Incident.id)).where(Incident.status == "resolved")
        )
        resolved_incidents = res_res.scalar() or 0

        avg_lat_res = await self.db.execute(
            select(func.avg(Incident.inference_latency_ms)).where(Incident.inference_latency_ms.isnot(None))
        )
        avg_latency = avg_lat_res.scalar() or 42.5

        since_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        vol_res = await self.db.execute(
            select(func.count(Incident.id)).where(Incident.created_at >= since_24h)
        )
        event_volume_24h = vol_res.scalar() or 0

        return SummaryMetric(
            total_cameras=total_cameras,
            active_cameras=active_cameras,
            total_incidents=total_incidents,
            open_incidents=open_incidents,
            critical_incidents=critical_incidents,
            resolved_incidents=resolved_incidents,
            avg_inference_latency_ms=round(float(avg_latency), 1),
            event_volume_24h=event_volume_24h,
        )

    async def get_trends(self, days: int = 7) -> list[TrendPoint]:
        sql = """
            SELECT to_char(created_at, 'YYYY-MM-DD') AS day,
                   COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE severity = 'critical') AS critical
            FROM incidents
            WHERE created_at >= NOW() - (:days || ' days')::interval
            GROUP BY day
            ORDER BY day ASC
        """
        rows = await self.db.execute(text(sql), {"days": days})
        return [
            TrendPoint(date=r[0], count=r[1], critical_count=r[2])
            for r in rows
        ]

    async def get_severity_distribution(self) -> list[SeverityCount]:
        sql = """
            SELECT severity, COUNT(*)
            FROM incidents
            GROUP BY severity
        """
        rows = await self.db.execute(text(sql))
        return [SeverityCount(severity=r[0], count=r[1]) for r in rows]

    async def get_camera_activity(self) -> list[CameraIncidentCount]:
        sql = """
            SELECT c.id::text, c.name, COUNT(i.id) AS count
            FROM cameras c
            LEFT JOIN incidents i ON c.id = i.camera_id
            GROUP BY c.id, c.name
            ORDER BY count DESC
            LIMIT 10
        """
        rows = await self.db.execute(text(sql))
        return [CameraIncidentCount(camera_id=r[0], camera_name=r[1], incident_count=r[2]) for r in rows]
