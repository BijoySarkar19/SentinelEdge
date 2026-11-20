import uuid
import structlog
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident
from app.models.detection_event import DetectionEvent
from app.models.outbox_event import OutboxEvent
from app.models.camera import Camera
from app.schemas.events import EdgeEventPayload
from app.schemas.incident import IncidentResponse
from app.repositories.incident import IncidentRepository
from app.repositories.camera import CameraRepository
from app.brokers.factory import get_event_broker
from app.websocket.manager import manager as ws_manager
from app.search.embedder import index_incident
from app.monitoring.metrics import INGESTED_EVENTS_TOTAL

logger = structlog.get_logger()

class IncidentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IncidentRepository(db)
        self.camera_repo = CameraRepository(db)

    async def ingest_edge_event(self, event: EdgeEventPayload) -> IncidentResponse:
        INGESTED_EVENTS_TOTAL.labels(
            event_type=event.event_type,
            severity=event.severity,
            simulated=str(event.simulated).lower(),
        ).inc()

        # Idempotency check
        existing = await self.repo.get_by_event_id(event.event_id)
        if existing:
            logger.info("Duplicate event ignored", event_id=event.event_id)
            return IncidentResponse.model_validate(existing)

        # Resolve camera UUID or create camera stub if not present
        cam_id: uuid.UUID
        try:
            cam_id = uuid.UUID(event.camera_id)
            camera = await self.camera_repo.get_by_id(cam_id)
            if not camera:
                cam = Camera(
                    id=cam_id,
                    name=f"Camera {event.camera_id[:8]}",
                    source_type="file" if event.simulated else "rtsp",
                    status="online",
                    processing_enabled=True,
                )
                self.db.add(cam)
                await self.db.commit()
        except ValueError:
            # Generate deterministic UUID for camera_id
            cam_id = uuid.uuid5(uuid.NAMESPACE_DNS, event.camera_id)
            camera = await self.camera_repo.get_by_id(cam_id)
            if not camera:
                cam = Camera(
                    id=cam_id,
                    name=f"Camera-{event.camera_id}",
                    source_type="file" if event.simulated else "rtsp",
                    status="online",
                    processing_enabled=True,
                )
                self.db.add(cam)
                await self.db.commit()

        # Resolve zone_id if passed
        z_id = None
        if event.zone_id:
            try:
                z_id = uuid.UUID(event.zone_id)
            except ValueError:
                z_id = uuid.uuid5(uuid.NAMESPACE_DNS, event.zone_id)

        # Build Incident
        incident = Incident(
            event_id=event.event_id,
            camera_id=cam_id,
            zone_id=z_id,
            title=event.summary.split(".")[0][:200],
            description=event.summary,
            severity=event.severity,
            status="open",
            confidence=event.confidence,
            latitude=event.latitude,
            longitude=event.longitude,
            object_counts=event.object_counts,
            detected_classes=event.detected_classes,
            inference_latency_ms=event.inference_latency_ms,
            simulated=event.simulated,
        )
        created = await self.repo.create(incident)

        # Outbox entry
        outbox = OutboxEvent(
            event_id=event.event_id,
            topic="sentinel.incidents",
            payload=event.model_dump(),
        )
        self.db.add(outbox)
        await self.db.commit()

        # Generate embedding asynchronously
        try:
            await index_incident(self.db, created)
        except Exception as e:
            logger.warning("Could not index incident embedding", error=str(e))

        # Real-time WebSocket broadcast
        await ws_manager.broadcast({
            "type": "incident_created",
            "data": {
                "id": str(created.id),
                "event_id": created.event_id,
                "title": created.title,
                "severity": created.severity,
                "status": created.status,
                "camera_id": str(created.camera_id),
                "confidence": created.confidence,
                "created_at": created.created_at.isoformat(),
                "simulated": created.simulated,
            }
        })

        # Broker publish
        try:
            broker = get_event_broker()
            await broker.publish("sentinel.incidents", str(created.id), event.model_dump())
        except Exception as e:
            logger.warning("Failed to publish to broker", error=str(e))

        return IncidentResponse.model_validate(created)

    async def get_incidents(
        self,
        skip: int = 0,
        limit: int = 50,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        camera_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[IncidentResponse], int]:
        incidents, total = await self.repo.get_all(skip, limit, severity, status, camera_id)
        return [IncidentResponse.model_validate(inc) for inc in incidents], total

    async def get_incident(self, incident_id: uuid.UUID) -> Optional[IncidentResponse]:
        inc = await self.repo.get_by_id(incident_id)
        if not inc:
            return None
        return IncidentResponse.model_validate(inc)

    async def update_status(
        self,
        incident_id: uuid.UUID,
        new_status: str,
        user_id: Optional[uuid.UUID] = None,
        comment: Optional[str] = None,
    ) -> Optional[IncidentResponse]:
        updated = await self.repo.update_status(incident_id, new_status, user_id, comment)
        if not updated:
            return None
        
        await ws_manager.broadcast({
            "type": "incident_updated",
            "data": {
                "id": str(updated.id),
                "status": updated.status,
                "updated_at": updated.updated_at.isoformat(),
            }
        })
        return IncidentResponse.model_validate(updated)
