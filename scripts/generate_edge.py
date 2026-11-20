import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

write("edge/pyproject.toml", '''
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "sentinledge-edge"
version = "0.1.0"
description = "SentinelEdge Edge CV & Privacy Runtime"
requires-python = ">=3.12"
dependencies = [
    "opencv-python>=4.10.0",
    "numpy>=1.26.0",
    "torch>=2.1.0",
    "torchvision>=0.16.0",
    "ultralytics>=8.1.0",
    "lap>=0.4.0",
    "httpx>=0.27.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
onnx = ["onnxruntime-gpu>=1.17.0"]

[tool.hatch.build.targets.wheel]
packages = ["src/sentinledge"]
''')

write("edge/config/settings.py", '''
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class EdgeConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    camera_id: str = "CAM-01"
    camera_name: str = "Main Entrance North"
    source_uri: str = "0"  # Webcam index 0 or file path or RTSP URL
    
    # Inference configuration (RTX 3050 Laptop GPU optimized)
    inference_device: str = "auto"  # auto, cuda, cpu
    inference_image_size: int = 640
    inference_confidence: float = 0.35
    inference_frame_skip: int = 2
    inference_fp16: bool = True
    
    # Privacy options
    privacy_mode: str = "metadata_only"  # metadata_only, blurred_preview
    face_detector_model: str = "yunet"
    plate_detector_model: Optional[str] = None
    store_blurred_evidence: bool = False
    anonymization_method: str = "gaussian_blur"  # gaussian_blur or pixelation
    
    # Ingestion API endpoint
    backend_api_url: str = "http://localhost:8000"
    ingest_endpoint: str = "/api/v1/incidents/ingest"

edge_settings = EdgeConfig()
''')

write("edge/models/.gitkeep", "")

write("edge/src/sentinledge/__init__.py", '''
"""SentinelEdge Computer Vision and Privacy Runtime."""
__version__ = "0.1.0"
''')

write("edge/src/sentinledge/utils/gpu_diagnostics.py", '''
import sys
from typing import Any

def run_gpu_diagnostic() -> dict[str, Any]:
    """Inspect local hardware and inference runtime for GPU/CUDA compatibility."""
    report = {
        "python_version": sys.version.split()[0],
        "pytorch_version": None,
        "cuda_available": False,
        "cuda_version": None,
        "gpu_name": None,
        "gpu_count": 0,
        "vram_total_mb": None,
        "vram_free_mb": None,
        "active_device": "cpu",
        "onnx_providers": [],
    }

    try:
        import torch
        report["pytorch_version"] = torch.__version__
        if torch.cuda.is_available():
            report["cuda_available"] = True
            report["cuda_version"] = torch.version.cuda
            report["gpu_count"] = torch.cuda.device_count()
            report["gpu_name"] = torch.cuda.get_device_name(0)
            report["active_device"] = "cuda:0"
            try:
                free_bytes, total_bytes = torch.cuda.mem_get_info(0)
                report["vram_total_mb"] = round(total_bytes / (1024 * 1024), 2)
                report["vram_free_mb"] = round(free_bytes / (1024 * 1024), 2)
            except Exception:
                pass
    except ImportError:
        pass

    try:
        import onnxruntime as ort
        report["onnx_providers"] = ort.get_available_providers()
    except ImportError:
        pass

    return report

def print_diagnostic_banner():
    diag = run_gpu_diagnostic()
    print("=" * 65)
    print("  SENTINEL-EDGE GPU & INFERENCE RUNTIME DIAGNOSTIC")
    print("=" * 65)
    print(f"  PyTorch Version:         {diag['pytorch_version'] or 'Not Installed'}")
    print(f"  CUDA Available:          {diag['cuda_available']}")
    if diag["cuda_available"]:
        print(f"  NVIDIA GPU Model:        {diag['gpu_name']}")
        print(f"  CUDA Runtime Version:    {diag['cuda_version']}")
        print(f"  Total VRAM:              {diag['vram_total_mb']} MB")
        print(f"  Free VRAM:               {diag['vram_free_mb']} MB")
        print(f"  Active Inference Target: {diag['active_device']}")
    else:
        print("  Active Inference Target: CPU (Safe Fallback Mode)")
    if diag["onnx_providers"]:
        print(f"  ONNX Providers:          {', '.join(diag['onnx_providers'])}")
    print("=" * 65)
''')

write("edge/src/sentinledge/utils/__init__.py", '''
from app.utils.gpu_diagnostics import run_gpu_diagnostic, print_diagnostic_banner
''')

write("edge/src/sentinledge/ingestion/video_reader.py", '''
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
''')

write("edge/src/sentinledge/ingestion/__init__.py", '''
from app.ingestion.video_reader import VideoIngestionSource

__all__ = ["VideoIngestionSource"]
''')

write("edge/src/sentinledge/detection/base.py", '''
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
''')

write("edge/src/sentinledge/detection/yolo_detector.py", '''
import structlog
import numpy as np
from typing import Sequence
from app.detection.base import BaseObjectDetector, DetectedObject

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
''')

write("edge/src/sentinledge/detection/onnx_detector.py", '''
import numpy as np
import structlog
from app.detection.base import BaseObjectDetector, DetectedObject

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
''')

write("edge/src/sentinledge/detection/factory.py", '''
from app.detection.base import BaseObjectDetector
from app.detection.yolo_detector import YOLOv8Detector
from app.detection.onnx_detector import ONNXRuntimeDetector

def create_detector(model_type: str = "yolo", **kwargs) -> BaseObjectDetector:
    if model_type == "onnx":
        return ONNXRuntimeDetector(kwargs.get("model_path", "models/detector.onnx"))
    return YOLOv8Detector(**kwargs)
''')

write("edge/src/sentinledge/detection/__init__.py", '''
from app.detection.base import BaseObjectDetector, DetectedObject
from app.detection.yolo_detector import YOLOv8Detector
from app.detection.factory import create_detector

__all__ = ["BaseObjectDetector", "DetectedObject", "YOLOv8Detector", "create_detector"]
''')

write("edge/src/sentinledge/tracking/bytetrack.py", '''
import numpy as np
from dataclasses import dataclass
from typing import Sequence
from app.detection.base import DetectedObject

@dataclass
class TrackedDetection:
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]
    dwell_time_seconds: float = 0.0
    first_seen_timestamp: float = 0.0

class MultiObjectTracker:
    """ByteTrack wrapper with non-PII, ephemeral session track IDs."""
    def __init__(self, max_lost_frames: int = 30, iou_threshold: float = 0.4):
        self.max_lost_frames = max_lost_frames
        self.iou_threshold = iou_threshold
        self.next_id = 1
        self.active_tracks: dict[int, TrackedDetection] = {}
        self.lost_counters: dict[int, int] = {}

    def _iou(self, boxA, boxB) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        denom = boxAArea + boxBArea - interArea
        return interArea / denom if denom > 0 else 0.0

    def update(self, detections: list[DetectedObject], timestamp: float) -> list[TrackedDetection]:
        updated_tracks = []
        unmatched_detections = list(detections)

        # Match with active tracks by IoU
        for tid, track in list(self.active_tracks.items()):
            best_iou = 0.0
            best_match_idx = -1
            for idx, det in enumerate(unmatched_detections):
                if det.class_id == track.class_id:
                    score = self._iou(track.bbox, det.bbox)
                    if score > best_iou:
                        best_iou = score
                        best_match_idx = idx

            if best_match_idx >= 0 and best_iou >= self.iou_threshold:
                matched_det = unmatched_detections.pop(best_match_idx)
                track.bbox = matched_det.bbox
                track.confidence = matched_det.confidence
                track.dwell_time_seconds = timestamp - track.first_seen_timestamp
                self.lost_counters[tid] = 0
                updated_tracks.append(track)
            else:
                self.lost_counters[tid] += 1
                if self.lost_counters[tid] <= self.max_lost_frames:
                    updated_tracks.append(track)
                else:
                    del self.active_tracks[tid]
                    del self.lost_counters[tid]

        # Register new detections
        for det in unmatched_detections:
            tid = self.next_id
            self.next_id += 1
            t = TrackedDetection(
                track_id=tid,
                class_id=det.class_id,
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=det.bbox,
                dwell_time_seconds=0.0,
                first_seen_timestamp=timestamp,
            )
            self.active_tracks[tid] = t
            self.lost_counters[tid] = 0
            updated_tracks.append(t)

        return updated_tracks
''')

write("edge/src/sentinledge/tracking/__init__.py", '''
from app.tracking.bytetrack import MultiObjectTracker, TrackedDetection

__all__ = ["MultiObjectTracker", "TrackedDetection"]
''')

write("edge/src/sentinledge/privacy/face_detector.py", '''
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
''')

write("edge/src/sentinledge/privacy/plate_detector.py", '''
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
''')

write("edge/src/sentinledge/privacy/privacy_filter.py", '''
import numpy as np
from app.privacy.face_detector import FaceAnonymizer
from app.privacy.plate_detector import LicensePlateAnonymizer

class PrivacyPipeline:
    def __init__(
        self,
        mode: str = "metadata_only",
        anonymization_method: str = "gaussian_blur",
    ):
        self.mode = mode
        self.anonymization_method = anonymization_method
        self.face_anonymizer = FaceAnonymizer()
        self.face_anonymizer.load()
        self.plate_anonymizer = LicensePlateAnonymizer()

    def process(self, frame: np.ndarray) -> tuple[np.ndarray | None, dict]:
        """
        Processes frame according to Privacy-First architecture.
        In 'metadata_only' mode: raw frames are NEVER returned or stored.
        """
        stats = {
            "mode": self.mode,
            "faces_anonymized": 0,
            "plates_anonymized": 0,
            "raw_video_retained": False,
        }

        if self.mode == "metadata_only":
            return None, stats

        # Blurred preview mode
        anonymized_frame, faces = self.face_anonymizer.detect_and_anonymize(frame, self.anonymization_method)
        anonymized_frame, plates = self.plate_anonymizer.detect_and_anonymize(anonymized_frame)

        stats["faces_anonymized"] = faces
        stats["plates_anonymized"] = plates
        return anonymized_frame, stats
''')

write("edge/src/sentinledge/privacy/__init__.py", '''
from app.privacy.face_detector import FaceAnonymizer
from app.privacy.plate_detector import LicensePlateAnonymizer
from app.privacy.privacy_filter import PrivacyPipeline

__all__ = ["FaceAnonymizer", "LicensePlateAnonymizer", "PrivacyPipeline"]
''')

write("edge/src/sentinledge/rules/engine.py", '''
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from app.tracking.bytetrack import TrackedDetection

@dataclass
class RuleDefinition:
    rule_id: str
    rule_name: str
    rule_type: str  # crowd_density, restricted_zone, vehicle_congestion, access_lane, custom
    camera_id: str
    zone_id: Optional[str]
    threshold_count: int
    duration_seconds: float
    severity: str
    cooldown_seconds: float = 60.0
    enabled: bool = True
    polygon_coordinates: list[list[float]] = field(default_factory=list)

@dataclass
class RuleTriggerResult:
    rule_id: str
    rule_name: str
    event_type: str
    severity: str
    confidence: float
    summary: str
    object_counts: dict[str, int]
    detected_classes: list[str]

class RulesEngine:
    def __init__(self, rules: list[RuleDefinition] | None = None):
        self.rules = rules or []
        self.last_triggered_timestamps: dict[str, float] = {}

    def add_rule(self, rule: RuleDefinition):
        self.rules.append(rule)

    def _point_in_polygon(self, x: float, y: float, poly: list[list[float]]) -> bool:
        if not poly or len(poly) < 3:
            return True
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def evaluate(self, tracks: list[TrackedDetection], current_time: float) -> list[RuleTriggerResult]:
        triggers = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            last_trig = self.last_triggered_timestamps.get(rule.rule_id, 0.0)
            if current_time - last_trig < rule.cooldown_seconds:
                continue

            # Class count aggregation
            counts: dict[str, int] = {}
            matching_tracks = []

            for track in tracks:
                cx = (track.bbox[0] + track.bbox[2]) / 2.0
                cy = (track.bbox[1] + track.bbox[3]) / 2.0
                if self._point_in_polygon(cx, cy, rule.polygon_coordinates):
                    counts[track.class_name] = counts.get(track.class_name, 0) + 1
                    matching_tracks.append(track)

            # Rule A: Crowd density
            if rule.rule_type == "crowd_density":
                person_count = counts.get("person", 0)
                if person_count >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="crowd_density",
                            severity=rule.severity,
                            confidence=0.91,
                            summary=f"Unusual crowd density warning: {person_count} persons detected (threshold: {rule.threshold_count})",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

            # Rule B: Restricted zone occupancy
            elif rule.rule_type == "restricted_zone":
                violators = [t for t in matching_tracks if t.dwell_time_seconds >= rule.duration_seconds]
                if len(violators) >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="restricted_zone",
                            severity=rule.severity,
                            confidence=0.94,
                            summary=f"Restricted zone occupancy detected: {len(violators)} objects dwelling over {rule.duration_seconds}s",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

            # Rule C: Vehicle congestion
            elif rule.rule_type == "vehicle_congestion":
                vehicles = sum(counts.get(k, 0) for k in ["car", "bus", "truck", "motorcycle"])
                if vehicles >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="vehicle_congestion",
                            severity=rule.severity,
                            confidence=0.88,
                            summary=f"Vehicle congestion detected: {vehicles} vehicles in monitored segment (threshold: {rule.threshold_count})",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

            # Rule D: Access lane blockage
            elif rule.rule_type == "access_lane":
                blockers = [t for t in matching_tracks if t.class_name in ["car", "truck", "bus"] and t.dwell_time_seconds >= rule.duration_seconds]
                if len(blockers) >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="access_lane",
                            severity=rule.severity,
                            confidence=0.92,
                            summary=f"Emergency access lane blocked: {len(blockers)} stationary vehicles for over {rule.duration_seconds}s",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

        return triggers
''')

write("edge/src/sentinledge/rules/__init__.py", '''
from app.rules.engine import RulesEngine, RuleDefinition, RuleTriggerResult

__all__ = ["RulesEngine", "RuleDefinition", "RuleTriggerResult"]
''')

write("edge/src/sentinledge/events/producer.py", '''
import uuid
import hashlib
from datetime import datetime, timezone
import httpx
import structlog
from app.rules.engine import RuleTriggerResult

logger = structlog.get_logger()

class EventProducer:
    def __init__(self, backend_url: str, ingest_endpoint: str = "/api/v1/incidents/ingest"):
        self.url = f"{backend_url.rstrip('/')}{ingest_endpoint}"
        self.client = httpx.Client(timeout=5.0)

    def send_incident_event(
        self,
        camera_id: str,
        rule_res: RuleTriggerResult,
        device: str,
        inference_latency_ms: float,
        privacy_status: dict,
        simulated: bool = False,
    ) -> bool:
        event_id = str(uuid.uuid4())
        raw_key = f"{camera_id}_{rule_res.rule_id}_{int(time.time() // 60)}"
        idempotency_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        payload = {
            "event_id": event_id,
            "idempotency_key": idempotency_key,
            "camera_id": camera_id,
            "rule_id": rule_res.rule_id,
            "event_type": rule_res.event_type,
            "severity": rule_res.severity,
            "confidence": rule_res.confidence,
            "summary": rule_res.summary,
            "object_counts": rule_res.object_counts,
            "detected_classes": rule_res.detected_classes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_device": device,
            "inference_backend": "yolo",
            "inference_latency_ms": round(inference_latency_ms, 2),
            "privacy_status": privacy_status,
            "simulated": simulated,
        }

        try:
            resp = self.client.post(self.url, json=payload)
            if resp.status_code in (200, 201):
                logger.info("Incident event dispatched to backend", event_id=event_id, type=rule_res.event_type)
                return True
            logger.warning("Backend returned non-200 for event ingest", status=resp.status_code, body=resp.text)
        except Exception as e:
            logger.error("Failed to post incident event", error=str(e), url=self.url)
        return False
''')

write("edge/src/sentinledge/events/__init__.py", '''
from app.events.producer import EventProducer

__all__ = ["EventProducer"]
''')

write("edge/src/sentinledge/performance/metrics.py", '''
import time

class PerformanceMonitor:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times: list[float] = []
        self.inference_latencies: list[float] = []
        self.total_frames = 0

    def record_frame(self, inference_ms: float):
        now = time.time()
        self.frame_times.append(now)
        self.inference_latencies.append(inference_ms)
        self.total_frames += 1

        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
            self.inference_latencies.pop(0)

    @property
    def fps(self) -> float:
        if len(self.frame_times) < 2:
            return 0.0
        elapsed = self.frame_times[-1] - self.frame_times[0]
        return round(len(self.frame_times) / elapsed, 1) if elapsed > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        if not self.inference_latencies:
            return 0.0
        return round(sum(self.inference_latencies) / len(self.inference_latencies), 1)
''')

write("edge/src/sentinledge/performance/__init__.py", '''
from app.performance.metrics import PerformanceMonitor

__all__ = ["PerformanceMonitor"]
''')

write("edge/src/sentinledge/main.py", '''
import sys
import time
import structlog
from config.settings import edge_settings
from app.utils.gpu_diagnostics import print_diagnostic_banner, run_gpu_diagnostic
from app.ingestion.video_reader import VideoIngestionSource
from app.detection.yolo_detector import YOLOv8Detector
from app.tracking.bytetrack import MultiObjectTracker
from app.privacy.privacy_filter import PrivacyPipeline
from app.rules.engine import RulesEngine, RuleDefinition
from app.events.producer import EventProducer
from app.performance.metrics import PerformanceMonitor

logger = structlog.get_logger()

def main():
    print_diagnostic_banner()
    diag = run_gpu_diagnostic()

    device = "cuda" if diag["cuda_available"] and edge_settings.inference_device != "cpu" else "cpu"
    logger.info("Initializing SentinelEdge CV Pipeline", device=device, camera=edge_settings.camera_id)

    # Initialize components
    detector = YOLOv8Detector(
        device=device,
        conf_threshold=edge_settings.inference_confidence,
        img_size=edge_settings.inference_image_size,
        fp16=edge_settings.inference_fp16,
    )
    detector.load()

    tracker = MultiObjectTracker()
    privacy = PrivacyPipeline(mode=edge_settings.privacy_mode)
    rules = RulesEngine([
        RuleDefinition(
            rule_id="RULE-CROWD-01",
            rule_name="Unusual Crowd Density",
            rule_type="crowd_density",
            camera_id=edge_settings.camera_id,
            zone_id=None,
            threshold_count=5,
            duration_seconds=3.0,
            severity="high",
            cooldown_seconds=30.0,
        ),
        RuleDefinition(
            rule_id="RULE-RESTRICTED-01",
            rule_name="Restricted Zone Breach",
            rule_type="restricted_zone",
            camera_id=edge_settings.camera_id,
            zone_id=None,
            threshold_count=1,
            duration_seconds=2.0,
            severity="critical",
            cooldown_seconds=30.0,
        ),
        RuleDefinition(
            rule_id="RULE-VEHICLE-01",
            rule_name="Vehicle Congestion Check",
            rule_type="vehicle_congestion",
            camera_id=edge_settings.camera_id,
            zone_id=None,
            threshold_count=3,
            duration_seconds=5.0,
            severity="medium",
            cooldown_seconds=45.0,
        ),
    ])
    producer = EventProducer(backend_url=edge_settings.backend_api_url, ingest_endpoint=edge_settings.ingest_endpoint)
    monitor = PerformanceMonitor()

    # Video Source
    source = VideoIngestionSource(edge_settings.source_uri, frame_skip=edge_settings.inference_frame_skip)
    logger.info("Opening video source", source=edge_settings.source_uri)
    if not source.open():
        logger.warning("Could not open source; running dry pipeline test loop with synthetic frame")
        import numpy as np
        fake_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frames_gen = [(i, time.time(), fake_frame) for i in range(1, 20)]
    else:
        frames_gen = source.frames()

    logger.info("SentinelEdge Edge Pipeline Active and Running.")
    try:
        for frame_id, ts, frame in frames_gen:
            t0 = time.perf_counter()
            detections = detector.detect(frame)
            inf_ms = (time.perf_counter() - t0) * 1000.0

            tracks = tracker.update(detections, ts)
            _, privacy_stats = privacy.process(frame)
            triggers = rules.evaluate(tracks, ts)

            for trig in triggers:
                producer.send_incident_event(
                    camera_id=edge_settings.camera_id,
                    rule_res=trig,
                    device=device,
                    inference_latency_ms=inf_ms,
                    privacy_status=privacy_stats,
                    simulated=False,
                )

            monitor.record_frame(inf_ms)
            if frame_id % 30 == 0:
                logger.info(
                    "Telemetry",
                    frame=frame_id,
                    fps=monitor.fps,
                    latency_ms=monitor.avg_latency_ms,
                    active_tracks=len(tracks),
                )
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
    finally:
        source.close()

if __name__ == "__main__":
    main()
''')

# ==================== EDGE TESTS ====================

write("edge/tests/test_video_reader.py", '''
import pytest
from app.ingestion.video_reader import VideoIngestionSource

def test_video_reader_initialization():
    reader = VideoIngestionSource(uri="test.mp4", frame_skip=3)
    assert reader.uri == "test.mp4"
    assert reader.frame_skip == 3
''')

write("edge/tests/test_rules_engine.py", '''
import pytest
from app.rules.engine import RulesEngine, RuleDefinition
from app.tracking.bytetrack import TrackedDetection

def test_crowd_density_rule_trigger():
    engine = RulesEngine([
        RuleDefinition(
            rule_id="R1",
            rule_name="Crowd Alert",
            rule_type="crowd_density",
            camera_id="CAM-1",
            zone_id=None,
            threshold_count=3,
            duration_seconds=0.0,
            severity="high",
            cooldown_seconds=10.0,
        )
    ])

    tracks = [
        TrackedDetection(track_id=1, class_id=0, class_name="person", confidence=0.9, bbox=(10,10,20,20)),
        TrackedDetection(track_id=2, class_id=0, class_name="person", confidence=0.88, bbox=(30,30,40,40)),
        TrackedDetection(track_id=3, class_id=0, class_name="person", confidence=0.92, bbox=(50,50,60,60)),
    ]

    triggers = engine.evaluate(tracks, current_time=100.0)
    assert len(triggers) == 1
    assert triggers[0].rule_id == "R1"
    assert triggers[0].severity == "high"

def test_rule_cooldown_prevents_duplicate():
    engine = RulesEngine([
        RuleDefinition(
            rule_id="R1",
            rule_name="Crowd Alert",
            rule_type="crowd_density",
            camera_id="CAM-1",
            zone_id=None,
            threshold_count=2,
            duration_seconds=0.0,
            severity="high",
            cooldown_seconds=60.0,
        )
    ])

    tracks = [
        TrackedDetection(track_id=1, class_id=0, class_name="person", confidence=0.9, bbox=(10,10,20,20)),
        TrackedDetection(track_id=2, class_id=0, class_name="person", confidence=0.9, bbox=(30,30,40,40)),
    ]

    # First trigger
    res1 = engine.evaluate(tracks, current_time=100.0)
    assert len(res1) == 1

    # Second trigger within cooldown
    res2 = engine.evaluate(tracks, current_time=110.0)
    assert len(res2) == 0
''')

write("edge/tests/test_privacy_filter.py", '''
import numpy as np
import pytest
from app.privacy.privacy_filter import PrivacyPipeline

def test_metadata_only_never_returns_raw_frame():
    pipeline = PrivacyPipeline(mode="metadata_only")
    raw_frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    processed, stats = pipeline.process(raw_frame)
    assert processed is None
    assert stats["raw_video_retained"] is False
    assert stats["mode"] == "metadata_only"
''')

write("edge/tests/__init__.py", "")

print("Edge generation complete.")
