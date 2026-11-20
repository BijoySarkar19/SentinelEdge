from abc import ABC, abstractmethod
from typing import Any, Optional

class EventBroker(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def publish(self, topic: str, key: str, payload: dict[str, Any]) -> str:
        pass
