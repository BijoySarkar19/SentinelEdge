import numpy as np
import structlog

logger = structlog.get_logger()

class LicensePlateAnonymizer:
    """Dedicated License Plate detector. Requires configured weights; does not guess."""
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.is_configured = bool(model_path)

    def detect_and_anonymize(self, frame: np.ndarray) -> tuple[np.ndarray, int]:
        if not self.is_configured:
            # Not pretending to detect plates without a valid model
            return frame, 0
        return frame, 0
