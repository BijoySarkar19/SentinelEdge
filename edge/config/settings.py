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
