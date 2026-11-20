from sentinledge.detection.base import BaseObjectDetector
from sentinledge.detection.yolo_detector import YOLOv8Detector
from sentinledge.detection.onnx_detector import ONNXRuntimeDetector

def create_detector(model_type: str = "yolo", **kwargs) -> BaseObjectDetector:
    if model_type == "onnx":
        return ONNXRuntimeDetector(kwargs.get("model_path", "models/detector.onnx"))
    return YOLOv8Detector(**kwargs)
