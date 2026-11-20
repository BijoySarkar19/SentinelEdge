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
