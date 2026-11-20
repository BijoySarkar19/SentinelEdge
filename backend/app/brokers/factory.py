from app.core.config import settings
from app.brokers.base import EventBroker
from app.brokers.redis_broker import RedisStreamsBroker
from app.brokers.kafka_broker import KafkaBroker

_broker_instance: EventBroker | None = None

def get_event_broker() -> EventBroker:
    global _broker_instance
    if _broker_instance is None:
        if settings.event_broker == "kafka":
            _broker_instance = KafkaBroker(settings.kafka_bootstrap_servers)
        else:
            _broker_instance = RedisStreamsBroker(settings.redis_url)
    return _broker_instance
