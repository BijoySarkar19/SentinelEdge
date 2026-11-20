import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== LICENSE ====================

write("LICENSE", """
SentinelEdge Project License

This software and custom architecture are licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.

Dependency Notice:
Certain edge computer-vision models such as Ultralytics YOLOv8 are governed by their respective
licenses (e.g., AGPL-3.0 or Enterprise licenses). Users must ensure compliance with model licenses
when deploying in production environments.
""")

# ==================== AGENTS.MD ====================

write("AGENTS.md", """# SentinelEdge Autonomous Engineering Log

This repository was architected and built using an iterative multi-agent engineering workflow:

- Architecture & Systems: Principal System Architect
- Edge Computer Vision: CV Engineer (OpenCV, YOLOv8n, ByteTrack, YuNet)
- Backend & Distributed Events: Senior Python Engineer (FastAPI, Redis Streams, pgvector)
- Frontend Operations: Full-Stack Developer (Next.js 15, React, Tailwind CSS, Leaflet)
- Security & Privacy: Privacy Engineer (Fail-safe anonymization, zero-raw-video edge policy)
""")

# ==================== ARCHITECTURE.MD ====================

write("docs/ARCHITECTURE.md", """# SentinelEdge Technical Architecture

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph EdgeDevice ["Edge Processing Node (RTX 3050 6GB / CPU)"]
        A[Camera / Video Source] --> B[Frame Ingestion & Skipping]
        B --> C[YOLOv8 Object Detection]
        C --> D[ByteTrack Multi-Object Tracking]
        D --> E[Privacy Anonymization Pipeline]
        E --> F[Configurable Rules Engine]
        F --> G[Structured Event Producer]
    end

    subgraph EventBroker ["Event Transportation Layer"]
        G -->|Edge Event Payload| H[Redis Streams / Optional Kafka]
    end

    subgraph BackendServices ["Backend Core Services"]
        H --> I[Event Consumer Worker]
        I --> J[PostgreSQL + pgvector Database]
        I --> K[Real-time WebSocket Manager]
        L[FastAPI REST API v1] --> J
        M[Sentence Transformers Embedder] --> J
    end

    subgraph FrontendApp ["Operator Control Center (Next.js 15)"]
        K --> N[Live Monitor & Event Stream]
        L --> O[GIS Map Dashboard]
        L --> P[Semantic Incident Search]
        L --> Q[Analytics & Rule Configuration]
    end
```

## 2. Edge-to-Cloud Privacy Boundary
SentinelEdge maintains a strict data boundary:
- Video frames NEVER leave the local edge device.
- All object bounding boxes, tracking associations, and face anonymization occur in local memory.
- Central ingestion endpoints accept only structured JSON incident metadata.
""")

# ==================== ROADMAP ====================

write("docs/EIGHT_WEEK_ROADMAP.md", """# SentinelEdge 8-Week Engineering Roadmap

> Note: This document outlines the planned continuous development schedule from MVP to enterprise production.

| Week | Focus Area | Core Deliverables | Success Criteria |
| :--- | :--- | :--- | :--- |
| **Week 1** | Foundation & CV Ingestion | OpenCV frame reader, PyTorch device verification, project monorepo structure | Video frames read smoothly with configurable frame skipping |
| **Week 2** | Detection & Multi-Object Tracking | YOLOv8n integration, ByteTrack tracker, tracking ID lifecycle | Moving objects accurately tracked without personal identification |
| **Week 3** | Privacy Engine & Incident Rules | Face & plate anonymizer, fail-safe mode, polygon zone rules | Faces blurred; crowd, congestion, and restricted zone rules firing |
| **Week 4** | Backend Core & Persistence | FastAPI endpoints, PostgreSQL models, Alembic migrations, Argon2 security | Incident metadata safely stored and searchable |
| **Week 5** | Distributed Event Pipeline | Redis Streams consumer groups, retry backoff, Dead-Letter Queue (DLQ) | Reliable asynchronous event processing under network dropouts |
| **Week 6** | Semantic Search & Web Console | pgvector sentence embeddings, Next.js 15 dashboard, Leaflet GIS map | Natural language queries like 'vehicle congestion near gate' return ranked results |
| **Week 7** | Performance & Hardening | RTX 3050 GPU optimization, FP16 execution, Prometheus/Grafana metrics | Sub-50ms inference latency; zero CUDA out-of-memory crashes |
| **Week 8** | Deployment & Production Readiness | Docker Compose multi-container setup, GitHub Actions CI/CD, documentation | One-click launch on target hardware with automated tests |
""")

# ==================== DATABASE SCHEMA ====================

write("docs/DATABASE_SCHEMA.md", """# SentinelEdge Database Schema

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : performs
    USERS ||--o{ INCIDENT_AUDITS : reviews
    CAMERAS ||--o{ ZONES : contains
    CAMERAS ||--o{ RULES : monitors
    CAMERAS ||--o{ INCIDENTS : captures
    INCIDENTS ||--o{ INCIDENT_AUDITS : tracks
    INCIDENTS ||--o| INCIDENT_EMBEDDINGS : indexed_by

    USERS {
        uuid id PK
        string username
        string email
        string password_hash
        string role
        boolean is_active
        timestamp created_at
    }

    CAMERAS {
        uuid id PK
        string name
        string source_type
        float latitude
        float longitude
        string status
        boolean processing_enabled
    }

    INCIDENTS {
        uuid id PK
        string event_id UK
        uuid camera_id FK
        uuid zone_id FK
        string title
        string severity
        string status
        float confidence
        json object_counts
        boolean simulated
        timestamp created_at
    }

    INCIDENT_EMBEDDINGS {
        uuid id PK
        uuid incident_id FK
        vector embedding
        string embedding_model
    }
```
""")

# ==================== PRIVACY & SECURITY ====================

write("docs/PRIVACY_AND_SECURITY.md", """# SentinelEdge Privacy & Security Architecture

## Core Architectural Guarantees

1. **Edge-Constrained Visual Data**:
   Video frames remain exclusively in temporary RAM on the edge processing device. No raw footage is transmitted to the central server or stored on disk by default.

2. **Automated Anonymization**:
   Faces and license plates are detected and blurred in memory prior to generating any optional preview thumbnails.

3. **No Biometric Identification**:
   Tracking IDs (e.g., Track-104) are ephemeral sequence numbers used exclusively for dwell-time and count calculation. The system performs NO facial recognition, emotion analysis, or demographic categorization.

4. **Fail-Safe Privacy Protection**:
   If an anonymization model fails or is unconfigured, the pipeline automatically locks down image output and switches to strict metadata-only mode.
""")

# ==================== THREAT MODEL ====================

write("docs/THREAT_MODEL.md", """# SentinelEdge Threat Model (STRIDE)

| Threat Vector | Attack Scenario | Implemented Mitigation | Residual Risk |
| :--- | :--- | :--- | :--- |
| **Credential Theft** | Brute force or sniffing of operator passwords | Argon2 password hashing, HTTP-only secure cookies, JWT expiration | Compromised operator workstation |
| **Event Spoofing** | Rogue edge nodes posting fabricated incident events | HMAC/token validation on `/api/v1/incidents/ingest`, IP whitelisting | Insider threat with API secret |
| **Duplicate Injection** | Network replays generating duplicate alerts | SHA-256 idempotency key deduplication in PostgreSQL and Redis | Storage overhead for idempotency window |
| **Raw Video Leak** | Unauthorized access to internal video feeds | Zero-upload edge architecture; raw streams never transit WAN | Physical tampering with edge hardware |
| **Denial of Service** | Flooding backend ingestion endpoint | SlowAPI rate limiting, reverse proxy limits, bounded Redis Streams | High edge bandwidth consumption |
""")

# ==================== GPU SETUP ====================

write("docs/GPU_SETUP.md", """# NVIDIA GPU Setup Guide (RTX 3050 Laptop 6GB)

## Prerequisites
- NVIDIA Graphics Driver version 535 or higher
- Windows 11 with WSL2 or Native Python 3.12

## Recommended PyTorch CUDA Installation
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Verification
Run the SentinelEdge GPU diagnostic utility:
```bash
python scripts/check_gpu.py
```

Expected Output on NVIDIA RTX 3050:
- CUDA Available: True
- GPU Model: NVIDIA GeForce RTX 3050 Laptop GPU
- Total VRAM: ~6144 MB
- Active Inference Target: cuda:0
""")

# ==================== BENCHMARK METHODOLOGY ====================

write("docs/BENCHMARK_METHODOLOGY.md", """# SentinelEdge Inference Benchmark Methodology

## Overview
The benchmark utility measures computer-vision inference latency under controlled conditions without fabricating results.

## Execution Command
```bash
python scripts/benchmark_inference.py --device cpu --frames 100
python scripts/benchmark_inference.py --device cuda --frames 100
```

## Metrics Collected
- **Average Latency**: Mean millisecond execution time per frame.
- **p50 / p95 / p99**: Percentile latency distributions indicating frame consistency.
- **Frames Per Second (FPS)**: Real-time throughput capability.
""")

# ==================== DEPLOYMENT ====================

write("docs/DEPLOYMENT.md", """# SentinelEdge Deployment Guide

## Quick Start with Docker
```bash
# 1. Start backend infrastructure (PostgreSQL, Redis, Prometheus, Grafana)
docker compose up -d

# 2. Check container health
docker compose ps
```

## Native Edge CV Launch
```bash
# Native edge launch avoids container GPU virtualization overhead
python edge/src/sentinledge/main.py --source 0
```
""")

# ==================== API REFERENCE ====================

write("docs/API_REFERENCE.md", """# SentinelEdge REST API Reference (v1)

Base URL: `/api/v1`

## Key Endpoints

- `POST /api/v1/auth/login`: Authenticate operator and set HTTP-only cookie.
- `GET /api/v1/cameras`: List all monitored camera nodes.
- `POST /api/v1/incidents/ingest`: Edge node event ingestion endpoint with idempotency.
- `GET /api/v1/incidents`: Retrieve paginated incidents with status and severity filters.
- `POST /api/v1/incidents/{id}/acknowledge`: Mark incident acknowledged by human operator.
- `POST /api/v1/incidents/{id}/resolve`: Resolve incident with resolution comment.
- `POST /api/v1/search/semantic`: Natural language incident search powered by pgvector.
- `GET /api/v1/analytics/summary`: Real-time KPI metrics.
- `GET /api/v1/health/ready`: Subsystem readiness probe.
""")

# ==================== MASTER README ====================

write("README.md", """# SentinelEdge

### Privacy-First Edge-to-Cloud Real-Time Video & Incident Intelligence Platform
*See the Risk. Protect the Privacy. Respond Intelligently.*

---

## Overview
Public spaces, commercial campuses, and industrial facilities deploy cameras that mostly record passive footage. SentinelEdge reduces manual operator workload by analyzing video locally at the edge, anonymizing visual data, and transmitting only structured metadata to an intelligent operations platform.

## Key Features
- **Assistive Computer Vision**: Object detection (YOLOv8n) and tracking (ByteTrack) for persons and vehicles.
- **Edge Privacy Guarantee**: Raw video is never uploaded; face blurring runs locally.
- **Custom Rules Engine**: Automated triggers for crowd density, restricted zone entry, congestion, and blocked access lanes.
- **Semantic Incident Search**: Natural language retrieval powered by PostgreSQL with pgvector.
- **Enterprise Web Dashboard**: Dark-mode Next.js 15 interface with interactive Leaflet GIS mapping and WebSocket telemetry.
- **Resilient Event Broker**: Redis Streams event processing with consumer groups, outbox pattern, and retries.

## Monorepo Layout
```text
SentinelEdge/
├── backend/          # FastAPI, SQLAlchemy 2.0, pgvector, Redis Streams
├── edge/             # Computer vision runtime, ByteTrack, privacy filters
├── frontend/         # Next.js 15 App Router, React, Tailwind CSS
├── infrastructure/   # Docker, PostgreSQL init, Redis, Prometheus, Grafana
├── scripts/          # GPU diagnostic, benchmarks, synthetic demo generator
└── docs/             # Architecture, threat model, roadmap, GPU setup
```

## Quick Start

### 1. Launch Backend Infrastructure (Docker)
```bash
docker compose up -d
```

### 2. Run Edge CV Processor (Native)
```bash
cd edge
python -m sentinledge.main --source 0
```

### 3. Launch Web Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) (Default user: `admin`).

## Hardware Optimization
Designed for laptops with NVIDIA RTX 3050 (6GB VRAM) running Windows 11, with seamless CPU fallback.
Verify setup using:
```bash
python scripts/check_gpu.py
```

## License
Licensed under the Apache License 2.0. Note model dependency licenses (e.g. Ultralytics AGPL-3.0) for commercial deployments.
""")

print("Documentation generated successfully.")
