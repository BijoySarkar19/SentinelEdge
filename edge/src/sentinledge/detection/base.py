from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence
import numpy as np

@dataclass
class DetectedObject:
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]  # [x1, y1, x2, y2] in pixels

class BaseObjectDetector(ABC):
    @abstractmethod
    def load(self) -> bool:
        pass

    @abstractmethod
    def detect(self, image: np.ndarray) -> list[DetectedObject]:
        pass
