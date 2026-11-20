import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== SEARCH / EMBEDDER ====================

write("backend/app/search/embedder.py", '''
import time
import structlog
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.config import settings
from app.models.incident import Incident
from app.models.incident_embedding import IncidentEmbedding
from app.schemas.search import SemanticSearchResultItem, SemanticSearchResponse
from app.monitoring.metrics import SEARCH_LATENCY

logger = structlog.get_logger()

_embed_model = None

def get_embedding_model():
    global _embed_model
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers embedding model", model=settings.embedding_model, device=settings.embedding_device)
            _embed_model = SentenceTransformer(settings.embedding_model, device=settings.embedding_device)
        except Exception as e:
            logger.warning("Failed to load sentence-transformers model; semantic search will use full-text fallback", error=str(e))
            _embed_model = False
    return _embed_model

def generate_embedding(text_content: str) -> Optional[list[float]]:
    model = get_embedding_model()
    if not model:
        return None
    try:
        vec = model.encode(text_content, normalize_embeddings=True)
        return vec.tolist()
    except Exception as e:
        logger.error("Error generating sentence embedding", error=str(e))
        return None

async def index_incident(db: AsyncSession, incident: Incident) -> None:
    text_content = f"{incident.title}. {incident.description or ''}"
    emb = generate_embedding(text_content)
    if not emb:
        return

    existing = await db.execute(
        select(IncidentEmbedding).where(IncidentEmbedding.incident_id == incident.id)
    )
    record = existing.scalar_one_or_none()
    if record:
        record.embedding = emb
    else:
        new_emb = IncidentEmbedding(
            incident_id=incident.id,
            embedding=emb,
            embedding_model=settings.embedding_model,
        )
        db.add(new_emb)
    await db.commit()

async def search_incidents(
    db: AsyncSession,
    query: str,
    limit: int = 10,
    severity: Optional[str] = None,
    camera_id: Optional[str] = None,
    status: Optional[str] = None,
) -> SemanticSearchResponse:
    start_time = time.perf_counter()
    emb = generate_embedding(query)
    results = []

    if emb:
        try:
            emb_str = "[" + ",".join(map(str, emb)) + "]"
            sql = """
                SELECT i.id, i.title, i.description, i.severity, i.status, i.confidence,
                       i.camera_id, i.created_at,
                       1 - (ie.embedding <=> (:query_vector)::vector) AS similarity
                FROM incidents i
                JOIN incident_embeddings ie ON i.id = ie.incident_id
                WHERE (:severity IS NULL OR i.severity = :severity)
                  AND (:camera_id IS NULL OR i.camera_id = :camera_id::uuid)
                  AND (:status IS NULL OR i.status = :status)
                ORDER BY similarity DESC
                LIMIT :limit
            """
            rows = await db.execute(
                text(sql),
                {
                    "query_vector": emb_str,
                    "severity": severity,
                    "camera_id": camera_id,
                    "status": status,
                    "limit": limit,
                },
            )
            for row in rows:
                results.append(
                    SemanticSearchResultItem(
                        incident_id=str(row[0]),
                        title=row[1],
                        description=row[2],
                        severity=row[3],
                        status=row[4],
                        confidence=float(row[5]),
                        camera_id=str(row[6]),
                        created_at=str(row[7]),
                        similarity_score=round(float(row[8]), 4),
                    )
                )
        except Exception as e:
            logger.warning("Vector search query failed, using text fallback", error=str(e))
            results = []

    if not results:
        # Full text search fallback
        sql = """
            SELECT id, title, description, severity, status, confidence, camera_id, created_at
            FROM incidents
            WHERE (title ILIKE :q OR description ILIKE :q)
              AND (:severity IS NULL OR severity = :severity)
              AND (:status IS NULL OR status = :status)
            ORDER BY created_at DESC
            LIMIT :limit
        """
        rows = await db.execute(
            text(sql),
            {
                "q": f"%{query}%",
                "severity": severity,
                "status": status,
                "limit": limit,
            },
        )
        for row in rows:
            results.append(
                SemanticSearchResultItem(
                    incident_id=str(row[0]),
                    title=row[1],
                    description=row[2],
                    severity=row[3],
                    status=row[4],
                    confidence=float(row[5]),
                    camera_id=str(row[6]),
                    created_at=str(row[7]),
                    similarity_score=0.5,
                )
            )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    SEARCH_LATENCY.observe(elapsed_ms / 1000.0)

    return SemanticSearchResponse(
        query=query,
        total=len(results),
        search_latency_ms=round(elapsed_ms, 2),
        results=results,
    )
''')

write("backend/app/search/__init__.py", '''
from app.search.embedder import search_incidents, index_incident, generate_embedding

__all__ = ["search_incidents", "index_incident", "generate_embedding"]
''')

# ==================== SERVICES ====================

write("backend/app/services/incident.py", '''
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
''')

write("backend/app/services/camera.py", '''
import uuid
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.repositories.camera import CameraRepository

class CameraService:
    def __init__(self, db: AsyncSession):
        self.repo = CameraRepository(db)

    async def list_cameras(self, skip: int = 0, limit: int = 100) -> list[CameraResponse]:
        cams = await self.repo.get_all(skip, limit)
        return [CameraResponse.model_validate(c) for c in cams]

    async def get_camera(self, camera_id: uuid.UUID) -> Optional[CameraResponse]:
        c = await self.repo.get_by_id(camera_id)
        if not c:
            return None
        return CameraResponse.model_validate(c)

    async def create_camera(self, camera_in: CameraCreate) -> CameraResponse:
        c = await self.repo.create(camera_in)
        return CameraResponse.model_validate(c)

    async def update_camera(self, camera_id: uuid.UUID, camera_in: CameraUpdate) -> Optional[CameraResponse]:
        c = await self.repo.update(camera_id, camera_in)
        if not c:
            return None
        return CameraResponse.model_validate(c)

    async def delete_camera(self, camera_id: uuid.UUID) -> bool:
        return await self.repo.delete(camera_id)
''')

write("backend/app/services/analytics.py", '''
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
''')

write("backend/app/services/__init__.py", '''
from app.services.incident import IncidentService
from app.services.camera import CameraService
from app.services.analytics import AnalyticsService

__all__ = ["IncidentService", "CameraService", "AnalyticsService"]
''')

# ==================== WORKERS ====================

write("backend/app/workers/event_consumer.py", '''
import asyncio
import json
import structlog
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.incident import IncidentService
from app.schemas.events import EdgeEventPayload
import redis.asyncio as aioredis

logger = structlog.get_logger()

async def run_redis_consumer():
    """Background worker consuming from Redis Streams with consumer groups."""
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    group = "sentinel_consumers"
    consumer_name = "worker_1"
    topic = "sentinel.incidents"

    try:
        await redis.xgroup_create(topic, group, id="0", mkstream=True)
    except Exception:
        pass

    logger.info("Starting Redis event consumer", topic=topic, group=group)

    while True:
        try:
            entries = await redis.xreadgroup(
                group,
                consumer_name,
                {topic: ">"},
                count=10,
                block=2000,
            )
            if entries:
                for stream, messages in entries:
                    for msg_id, data in messages:
                        try:
                            payload_raw = json.loads(data.get("payload", "{}"))
                            event = EdgeEventPayload(**payload_raw)
                            async with AsyncSessionLocal() as db:
                                service = IncidentService(db)
                                await service.ingest_edge_event(event)
                            await redis.xack(topic, group, msg_id)
                        except Exception as e:
                            logger.error("Consumer processing error", error=str(e), msg_id=msg_id)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Consumer loop exception", error=str(e))
            await asyncio.sleep(2)

    await redis.close()
''')

write("backend/app/workers/outbox_worker.py", '''
import asyncio
from datetime import datetime, timezone
import structlog
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.outbox_event import OutboxEvent
from app.brokers.factory import get_event_broker

logger = structlog.get_logger()

async def run_outbox_publisher():
    """Background outbox processor ensuring reliable event delivery."""
    logger.info("Starting transactional outbox publisher")
    broker = get_event_broker()

    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(OutboxEvent)
                    .where(OutboxEvent.published_at.is_(None))
                    .limit(50)
                )
                events = result.scalars().all()
                for ev in events:
                    try:
                        await broker.publish(ev.topic, ev.event_id, ev.payload)
                        ev.published_at = datetime.now(timezone.utc)
                    except Exception as e:
                        ev.retry_count += 1
                        logger.warning("Outbox publish retry", error=str(e), event_id=ev.event_id)
                await db.commit()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Outbox worker loop error", error=str(e))
        await asyncio.sleep(5)
''')

write("backend/app/workers/__init__.py", '''
from app.workers.event_consumer import run_redis_consumer
from app.workers.outbox_worker import run_outbox_publisher

__all__ = ["run_redis_consumer", "run_outbox_publisher"]
''')

print("Backend Part 3 (services, search, workers) complete.")
