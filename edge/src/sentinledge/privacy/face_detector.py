import cv2
import numpy as np
import structlog

logger = structlog.get_logger()

class FaceAnonymizer:
    """Modular Face Detection and Obfuscation."""
    def __init__(self, model_name: str = "yunet"):
        self.model_name = model_name
        self.detector = None
        self.is_ready = False

    def load(self) -> bool:
        try:
            # OpenCV YuNet face detector initialization if weights available
            self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.is_ready = not self.detector.empty()
            return self.is_ready
        except Exception as e:
            logger.warning("Could not initialize face detection cascade", error=str(e))
            self.is_ready = False
            return False

    def detect_and_anonymize(self, frame: np.ndarray, method: str = "gaussian_blur") -> tuple[np.ndarray, int]:
        if not self.is_ready or self.detector is None:
            return frame, 0

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
            if len(faces) == 0:
                return frame, 0

            out = frame.copy()
            for (x, y, w, h) in faces:
                x1, y1 = max(0, x), max(0, y)
                x2, y2 = min(frame.shape[1], x + w), min(frame.shape[0], y + h)
                roi = out[y1:y2, x1:x2]
                if roi.size > 0:
                    if method == "pixelation":
                        small = cv2.resize(roi, (8, 8), interpolation=cv2.INTER_LINEAR)
                        out[y1:y2, x1:x2] = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                    else:
                        out[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (51, 51), 30)
            return out, len(faces)
        except Exception as e:
            logger.error("Face anonymization error", error=str(e))
            return frame, 0
