import json
import structlog
from typing import Any
import redis.asyncio as aioredis
from app.brokers.base import EventBroker
from app.core.config import settings

logger = structlog.get_logger()

class RedisStreamsBroker(EventBroker):
    def __init__(self, url: str):
        self.url = url
        self.redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        if not self.redis:
            self.redis = aioredis.from_url(self.url, decode_responses=True)
            logger.info("Connected to Redis Streams", url=self.url)

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def publish(self, topic: str, key: str, payload: dict[str, Any]) -> str:
        await self.connect()
        data = {
            "key": key,
            "payload": json.dumps(payload),
        }
        msg_id = await self.redis.xadd(topic, data)
        return str(msg_id)

    async def ensure_consumer_group(self, topic: str, group: str) -> None:
        await self.connect()
        try:
            await self.redis.xgroup_create(topic, group, id="0", mkstream=True)
            logger.info("Created consumer group", group=group, topic=topic)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                logger.warning("Error creating consumer group", error=str(e))
