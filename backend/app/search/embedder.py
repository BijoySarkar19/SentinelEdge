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
