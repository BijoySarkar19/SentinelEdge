import time
from typing import Generator, Optional, Tuple
import cv2
import numpy as np

class VideoIngestionSource:
    def __init__(self, uri: str | int, frame_skip: int = 2):
        self.uri = uri
        self.frame_skip = max(0, frame_skip)
        self.cap: Optional[cv2.VideoCapture] = None
        self.fps: float = 30.0
        self.width: int = 1280
        self.height: int = 720
        self.frame_id: int = 0

    def open(self) -> bool:
        src = int(self.uri) if str(self.uri).isdigit() else str(self.uri)
        self.cap = cv2.VideoCapture(src)
        if not self.cap or not self.cap.isOpened():
            return False
        
        detected_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if detected_fps and detected_fps > 0:
            self.fps = detected_fps
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or self.width
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or self.height
        return True

    def frames(self) -> Generator[Tuple[int, float, np.ndarray], None, None]:
        if not self.cap or not self.cap.isOpened():
            if not self.open():
                return

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                break

            self.frame_id += 1
            if self.frame_skip > 0 and (self.frame_id % (self.frame_skip + 1) != 0):
                continue

            timestamp = time.time()
            yield self.frame_id, timestamp, frame

    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None
