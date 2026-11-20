# SentinelEdge — Operator & User Manual

Welcome to **SentinelEdge**, the Privacy-First Edge-to-Cloud Real-Time Video & Incident Intelligence Platform.

---

## 1. Quick Access & Credentials

- **Web Console URL:** [http://localhost:3000](http://localhost:3000) (or [http://localhost](http://localhost) in production)
- **API Documentation:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Telemetry Dashboards:** [http://localhost:3001](http://localhost:3001)

### Default Operator Credentials
- **Username:** `admin`
- **Password:** `Admin@Sentinel2026!`

---

## 2. Navigating the Dashboard (`/dashboard`)

The **Operational Overview** gives operators an instant bird's-eye view of site safety and edge inference health:

1. **KPI Stat Cards**:
   - **Monitored Cameras:** Total online camera nodes reporting telemetry.
   - **Open Incidents:** Active alerts requiring operator action (highlighted in amber/red).
   - **Avg Inference Latency:** Milliseconds per frame (benchmarked at ~41 ms / 24 FPS on NVIDIA RTX Laptop GPU or CPU).
   - **Privacy Guard:** Confirms that metadata-only edge transmission is active (100% WAN privacy protection).
2. **Incident Trajectory Chart:** Visualizes 7-day alert volumes split by total volume and critical alerts.
3. **Severity Breakdown:** Color-coded distribution across Critical, High, Medium, and Low alerts.
4. **Live Edge Event Stream:** Real-time stream of incoming incident events pushed over WebSockets.

---

## 3. Live Edge Monitoring (`/live-monitor`)

Visit `/live-monitor` to inspect live video feeds:

- **Privacy-Preserving Feeds:** Shows edge-filtered synthetic video streams where human faces are blurred or rendered in metadata-only bounding boxes.
- **Hardware Telemetry Overlay:** Real-time FPS, hardware target (`cuda:0` or `cpu`), and active tracked object counts per camera.
- **Node Status:** Indicates whether the camera node is actively processing, standby, or offline.

---

## 4. Camera Node Management (`/cameras`)

Visit `/cameras` to view and configure video input sources:

- **Source Types Supported:**
  - `rtsp`: Network IP security cameras (`rtsp://user:pass@192.168.1.100:554/stream1`)
  - `webcam`: USB / Integrated video capture (`0`, `1`)
  - `file`: MP4 / AVI test video files for offline simulation
- **Actions:** Add new camera nodes, update geographical locations, and toggle edge processing on or off.

---

## 5. Incident Management & Triage (`/incidents`)

The incident tracker handles the complete alert lifecycle:

### Triage Workflow
1. **Open Alert:** An incoming alert arrives with confidence score and object count.
2. **Acknowledge:** Click **Acknowledge** to take ownership of the alert (updates status to `acknowledged`).
3. **Investigate:** Click **Mark Investigating** when initiating radio contact or dispatching personnel.
4. **Resolve / False Positive:** Click **Resolve Incident** with an optional operator comment to close the incident and commit to the tamper-evident audit log.

### Incident Detail View (`/incidents/[id]`)
- Inspect detection bounding boxes, timestamp, camera coordinates, and dwell time.
- Review complete **Audit Trail History** showing which operator changed statuses and when.

---

## 6. Natural Language / Semantic Search (`/search`)

Powered by **pgvector** and 384-dimensional sentence embeddings:

- Type natural human language queries into the search bar:
  - *"unusual crowd gathering near entrance"*
  - *"delivery vehicle blocking emergency fire lane"*
  - *"chemical hazmat storage breach"*
  - *"nighttime loitering alert"*
- **Results:** Instantly ranks incidents by mathematical cosine similarity score with sub-50ms latency.
- **Zero-Error Fallback:** Automatically degrades to intelligent multi-word keyword search if vector embeddings are temporarily unavailable.

---

## 7. Rules Engine Configuration (`/rules`)

Customize automated incident triggers:

- **Rule Types:**
  - `crowd_density`: Triggers when people count exceeds a set threshold (e.g. > 8 persons).
  - `restricted_zone`: Triggers when any tracked object enters a prohibited polygon.
  - `vehicle_congestion`: Triggers when vehicles remain stationary in traffic corridors.
  - `access_lane`: Triggers when emergency egress or fire lanes are blocked.
- **Parameters:** Configurable minimum dwell duration (seconds), polygon zone, and target severity.

---

## 8. Geospatial Intelligence Map (`/map`)

- **Interactive Canvas Map:** Built-in vector map rendering sector zones, access lanes, camera positions, and alert markers.
- **Zero External Dependencies:** Renders instantly in air-gapped intranets with zero external map tile failures.

---

## 9. System Diagnostics & Settings (`/system`, `/settings`)

- **Diagnostics:** Probes live latency for PostgreSQL, Redis Streams, Sentence Transformers, and Edge CV detection.
- **Settings:** Set incident data retention windows (days) and configure inference hardware preferences (`auto`, `cuda`, `cpu`).
