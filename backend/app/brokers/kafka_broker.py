import json
import structlog
from typing import Any
from app.brokers.base import EventBroker

logger = structlog.get_logger()

class KafkaBroker(EventBroker):
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def connect(self) -> None:
        try:
            from aiokafka import AIOKafkaProducer
            if not self.producer:
                self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
                await self.producer.start()
                logger.info("Connected to Redpanda/Kafka", servers=self.bootstrap_servers)
        except ImportError:
            logger.warning("aiokafka not installed; falling back to stub mode")

    async def disconnect(self) -> None:
        if self.producer:
            await self.producer.stop()
            self.producer = None

    async def publish(self, topic: str, key: str, payload: dict[str, Any]) -> str:
        await self.connect()
        if self.producer:
            encoded_val = json.dumps(payload).encode("utf-8")
            encoded_key = key.encode("utf-8")
            record = await self.producer.send_and_wait(topic, key=encoded_key, value=encoded_val)
            return f"{record.offset}"
        logger.info("[Kafka Stub] Published", topic=topic, key=key)
        return "stub-offset"
