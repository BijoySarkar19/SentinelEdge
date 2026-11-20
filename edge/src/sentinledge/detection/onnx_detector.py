import numpy as np
import structlog
from sentinledge.detection.base import BaseObjectDetector, DetectedObject

logger = structlog.get_logger()

class ONNXRuntimeDetector(BaseObjectDetector):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.session = None

    def load(self) -> bool:
        try:
            import onnxruntime as ort
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            logger.info("Loaded ONNX Runtime session", providers=self.session.get_providers())
            return True
        except Exception as e:
            logger.warning("Could not load ONNX model", error=str(e))
            return False

    def detect(self, image: np.ndarray) -> list[DetectedObject]:
        return []
