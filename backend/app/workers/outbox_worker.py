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
