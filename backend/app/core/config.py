"""Application configuration via Pydantic Settings v2."""
from __future__ import annotations

from pydantic import Field, AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object.  Values are read from environment variables
    and/or a ``.env`` file in the working directory."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_env: str = Field(default="development", description="Runtime environment (development | staging | production)")
    log_level: str = Field(default="INFO", description="Python logging level")

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://sentinel:sentinelpass@localhost:5432/sentineledge",
        description="Async SQLAlchemy database URL (asyncpg driver)",
    )

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL used for caching and pub/sub",
    )

    # ------------------------------------------------------------------
    # JWT / Auth
    # ------------------------------------------------------------------
    jwt_secret_key: str = Field(
        default="change-this",
        description="Secret key used to sign JWT tokens.  MUST be overridden in production.",
    )
    jwt_algorithm: str = Field(default="HS256", description="HMAC algorithm for JWT signing")
    access_token_expire_minutes: int = Field(default=60, ge=1, description="Access token TTL in minutes")
    refresh_token_expire_days: int = Field(default=7, ge=1, description="Refresh token TTL in days")

    # ------------------------------------------------------------------
    # Admin bootstrap
    # ------------------------------------------------------------------
    bootstrap_admin_username: str = Field(default="admin", description="Username for the auto-created admin account")
    bootstrap_admin_email: str = Field(
        default="admin@sentineledge.local",
        description="E-mail for the auto-created admin account",
    )
    bootstrap_admin_password: str = Field(
        default="",
        description="Plain-text password for the auto-created admin account.  Empty = skip bootstrap.",
    )

    # ------------------------------------------------------------------
    # Event broker
    # ------------------------------------------------------------------
    event_broker: str = Field(default="redis", description="Event broker backend: 'redis' or 'kafka'")
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Comma-separated Kafka bootstrap server list (used when event_broker='kafka')",
    )

    # ------------------------------------------------------------------
    # Embedding / NLP
    # ------------------------------------------------------------------
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace model identifier for sentence embeddings",
    )
    embedding_device: str = Field(
        default="cpu",
        description="Torch device for embedding inference ('cpu' | 'cuda' | 'mps')",
    )

    # ------------------------------------------------------------------
    # Edge inference
    # ------------------------------------------------------------------
    inference_device: str = Field(
        default="auto",
        description="Torch device for object-detection inference ('auto' | 'cpu' | 'cuda' | 'mps')",
    )
    inference_image_size: int = Field(default=640, ge=320, le=1280, description="Input image size for YOLO inference")
    inference_confidence: float = Field(
        default=0.35, ge=0.0, le=1.0, description="Minimum confidence threshold for detections"
    )
    inference_frame_skip: int = Field(default=2, ge=0, description="Number of frames to skip between inferences")
    inference_fp16: bool = Field(default=False, description="Use FP16 (half-precision) for inference when supported")
    yolo_model: str = Field(default="yolov8n.pt", description="YOLO model weights file or HuggingFace identifier")

    # ------------------------------------------------------------------
    # Privacy / PII
    # ------------------------------------------------------------------
    face_detector_model: str = Field(
        default="yunet",
        description="Face detection backend used for blurring ('yunet' | 'mediapipe')",
    )
    plate_detector_model: str = Field(
        default="",
        description="License-plate detection model file path (empty = disabled)",
    )
    privacy_mode: str = Field(
        default="metadata_only",
        description="Privacy mode: 'metadata_only' | 'blur' | 'full_redact'",
    )
    store_blurred_evidence: bool = Field(
        default=False,
        description="Persist blurred frames to object storage for audit trails",
    )
    retention_days: int = Field(default=30, ge=1, description="Number of days to retain event records")

    # ------------------------------------------------------------------
    # Frontend / CORS
    # ------------------------------------------------------------------
    frontend_url: str = Field(default="http://localhost:3000", description="Public URL of the frontend application")
    api_base_url: str = Field(default="http://localhost:8000", description="Public base URL of this API")
    cors_origins: list[str] | str = Field(
        default=["http://localhost:3000"],
        description="List of allowed CORS origins",
    )

    # ------------------------------------------------------------------
    # Rate limiting (slowapi / Redis)
    # ------------------------------------------------------------------
    rate_limit_requests: int = Field(default=100, ge=1, description="Max requests per window per client IP")
    rate_limit_window: int = Field(default=60, ge=1, description="Rate-limit sliding window in seconds")

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}, got '{v}'")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got '{v}'")
        return upper

    @field_validator("privacy_mode")
    @classmethod
    def validate_privacy_mode(cls, v: str) -> str:
        allowed = {"metadata_only", "blur", "full_redact"}
        if v not in allowed:
            raise ValueError(f"privacy_mode must be one of {allowed}, got '{v}'")
        return v

    # ------------------------------------------------------------------
    # Computed helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        """Return True when running in the production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Return True when running in the development environment."""
        return self.app_env == "development"

    @property
    def access_token_expire_seconds(self) -> int:
        """Access token TTL expressed in seconds (convenience helper)."""
        return self.access_token_expire_minutes * 60


# ---------------------------------------------------------------------------
# Module-level singleton – import this everywhere:  from app.core.config import settings
# ---------------------------------------------------------------------------
settings = Settings()
