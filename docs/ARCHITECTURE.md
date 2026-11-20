# SentinelEdge Technical Architecture

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
