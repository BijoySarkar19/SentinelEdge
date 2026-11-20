# =============================================================================
# SentinelEdge — FastAPI Backend Dockerfile
# Multi-stage build: builder installs deps; runtime is a lean final image.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder: install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system-level build tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc \
      g++ \
      libpq-dev \
      libffi-dev \
      libssl-dev \
      curl \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build backend
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy dependency manifest(s) first for layer caching
COPY pyproject.toml .
COPY README.md* ./

# Install the project and all its dependencies into the system site-packages
RUN pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Stage 2 — Runtime: minimal production image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

LABEL maintainer="SentinelEdge Team"
LABEL org.opencontainers.image.title="SentinelEdge Backend"
LABEL org.opencontainers.image.description="FastAPI + pgvector + Redis edge-to-cloud video intelligence backend"
LABEL org.opencontainers.image.version="0.1.0"

WORKDIR /app

# Install only runtime system libraries (no build tools)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpq5 \
      libgomp1 \
      curl \
 && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY . .

# Create a non-root user for security
RUN groupadd --system --gid 1001 sentinel \
 && useradd  --system --uid 1001 --gid sentinel --no-create-home sentinel \
 && chown -R sentinel:sentinel /app

USER sentinel

EXPOSE 8000

# Health check — hits the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=30s \
  CMD curl -f http://localhost:8000/health || exit 1

# Production command (override in compose.yaml for --reload in dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
