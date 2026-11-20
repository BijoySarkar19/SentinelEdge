import structlog
import numpy as np
from typing import Sequence
from sentinledge.detection.base import BaseObjectDetector, DetectedObject

logger = structlog.get_logger()

# Standard target COCO classes
TARGET_CLASSES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

class YOLOv8Detector(BaseObjectDetector):
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        device: str = "auto",
        conf_threshold: float = 0.35,
        img_size: int = 640,
        fp16: bool = True,
    ):
        self.model_name = model_name
        self.requested_device = device
        self.conf_threshold = conf_threshold
        self.img_size = img_size
        self.fp16 = fp16
        self.model = None
        self.device = "cpu"

    def load(self) -> bool:
        try:
            import torch
            from ultralytics import YOLO

            if self.requested_device == "auto":
                self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            else:
                self.device = self.requested_device

            self.model = YOLO(self.model_name)
            logger.info("Loaded YOLOv8 model", model=self.model_name, device=self.device)
            return True
        except Exception as e:
            logger.warning("Could not load YOLOv8 model, using mock fallback detector", error=str(e))
            self.model = None
            return False

    def detect(self, image: np.ndarray) -> list[DetectedObject]:
        if self.model is None:
            # Synthetic / fallback detection for testing without model download
            h, w = image.shape[:2]
            return [
                DetectedObject(
                    class_id=0,
                    class_name="person",
                    confidence=0.89,
                    bbox=(w * 0.2, h * 0.3, w * 0.4, h * 0.8),
                )
            ]

        try:
            results = self.model.predict(
                source=image,
                conf=self.conf_threshold,
                imgsz=self.img_size,
                device=self.device,
                half=self.fp16 and self.device.startswith("cuda"),
                verbose=False,
            )
            detections = []
            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    if cls_id in TARGET_CLASSES:
                        conf = float(box.conf[0].item())
                        xyxy = box.xyxy[0].tolist()
                        detections.append(
                            DetectedObject(
                                class_id=cls_id,
                                class_name=TARGET_CLASSES[cls_id],
                                confidence=round(conf, 3),
                                bbox=(xyxy[0], xyxy[1], xyxy[2], xyxy[3]),
                            )
                        )
            return detections
        except Exception as e:
            logger.error("YOLO inference error", error=str(e))
            return []
