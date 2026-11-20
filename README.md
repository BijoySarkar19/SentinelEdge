# SentinelEdge

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
