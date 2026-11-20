# =============================================================================
# SentinelEdge — Edge CV & Privacy Runtime Dockerfile
# Optimized for real-time computer vision inference & privacy anonymization
# =============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch (CPU build by default for Docker portability, or CUDA if GPU runtime used)
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining vision and event dependencies
RUN pip install --no-cache-dir \
    opencv-python-headless \
    numpy \
    ultralytics \
    lap \
    httpx \
    pydantic \
    pydantic-settings \
    structlog

# Copy edge source code
COPY pyproject.toml .
COPY config/ ./config/
COPY src/ ./src/
COPY models/ ./models/

# Install the edge package in editable mode
RUN pip install --no-cache-dir -e .

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:/app
ENV BACKEND_API_URL=http://backend:8000
ENV INGEST_ENDPOINT=/api/v1/incidents/ingest
ENV INFERENCE_DEVICE=cpu
ENV PRIVACY_MODE=metadata_only
ENV SOURCE_URI=0

CMD ["python", "src/sentinledge/main.py"]
