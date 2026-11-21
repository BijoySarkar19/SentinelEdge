# SentinelEdge Enterprise Privacy Policy & Data Processing Notice

**Effective Date:** November 21, 2026  
**Document Version:** 1.0.0  
**Jurisdiction:** Global (Standardized for GDPR, CCPA/CPRA, and EU AI Act Compliance)

---

## 1. Executive Summary & Privacy-First Philosophy

SentinelEdge is architected under the principle of **Privacy by Design and by Default** (Article 25, EU General Data Protection Regulation - GDPR). Unlike conventional Closed-Circuit Television (CCTV) or cloud-based Video Surveillance as a Service (VSaaS) platforms, SentinelEdge operates on an **in-memory, edge-constrained, metadata-only paradigm**. 

**The fundamental privacy guarantee of SentinelEdge is:**
> **Zero Raw Video WAN Transmission:** High-resolution video streams are processed exclusively in volatile random-access memory (RAM) directly on edge hardware. Raw footage is never transmitted across Wide Area Networks (WAN), uploaded to central cloud servers, or stored on persistent central disks.

---

## 2. Roles and Classifications

To ensure compliance with international data privacy regulations:
* **The Deploying Entity / Customer is the "Data Controller":** The organization (enterprise, facility operator, educational institution, or property manager) that installs SentinelEdge, positions camera sensors, and defines detection zones is the Data Controller. The Controller is responsible for establishing the lawful basis for surveillance and providing statutory notification to individuals on premise.
* **The SentinelEdge Platform is the "Data Processor / Processing Software":** SentinelEdge provides the technological mechanisms (computer vision models, redaction filters, rules engine, and vector search) used by the Data Controller to analyze spatial incidents while enforcing strict data minimization.

---

## 3. Categories of Data Processed

### 3.1. Data Processed Temporarily at the Edge (Never Uploaded)
* **Raw Video Frames:** Transient digital frames captured from RTSP, USB, or IP camera feeds. These frames exist solely within GPU/CPU memory for the duration of inference (~15–45 milliseconds) and are immediately overwritten by subsequent frames.
* **Facial Imagery & License Plates:** PII (Personally Identifiable Information) detected in any frame is subjected to automated in-memory Gaussian blurring or pixelization *before* any incident snapshot is generated.

### 3.2. Data Stored & Transmitted to Central Central Systems (Incident Metadata Only)
When an authorized rule is triggered (e.g., loitering in a restricted hazard zone), SentinelEdge transmits strictly non-PII, structured incident telemetry:
1. **Temporal Data:** Event timestamp (ISO 8601 UTC) and dwell duration.
2. **Spatial Data:** Camera identifier, polygon zone ID, normalized bounding-box coordinates `[x_min, y_min, x_max, y_max]`.
3. **Statistical Counts:** Object classification categories (`person`, `car`, `truck`, `bicycle`) and quantity counts (e.g., `object_counts: {"person": 2}`).
4. **Model Metrics:** Detection confidence score (e.g., `0.94`), inference latency in milliseconds, and hardware target identifier (`cuda:0` / `cpu`).
5. **Mathematical Vector Embeddings:** 384-dimensional dense numerical float arrays generated from incident textual descriptions via local sentence-transformers models, stored in PostgreSQL via `pgvector` for semantic querying.
6. **Privacy-Redacted Previews (Optional):** If configured by the Data Controller, privacy-redacted thumbnails with faces and vehicle plates permanently obscured may be attached to incident audit trails.

### 3.3. Strictly Prohibited & Uncollected Data
* **No Facial Recognition:** The platform does not extract, store, or match facial biometric templates against watchlists.
* **No Demographic or Emotion Profiling:** The models do not infer race, gender, age, health, emotional state, or physical characteristics.
* **No Cross-Facility Tracking:** Tracking identifiers (e.g., `Track-104`) assigned by ByteTrack are ephemeral sequence numbers destroyed as soon as an entity exits the single camera field-of-view.

---

## 4. Lawful Bases for Processing (GDPR Article 6)

Data Controllers deploying SentinelEdge typically rely on the following lawful bases:
1. **Legitimate Interests (GDPR Art. 6(1)(f)):** Protecting physical assets, securing perimeters, preventing trespassing, and ensuring worker health and safety in hazardous environments.
2. **Vital Interests (GDPR Art. 6(1)(d)):** Ensuring emergency evacuation corridors and fire lanes remain clear of obstruction, and detecting life-safety risks in industrial plants.
3. **Legal Obligation (GDPR Art. 6(1)(c)):** Complying with industrial safety codes, chemical plant security standards, or critical infrastructure protection regulations.

---

## 5. Technical and Organizational Measures (TOMs)

SentinelEdge incorporates robust technical safeguards as required by GDPR Article 32:
* **Fail-Safe Privacy Lockdown:** If the in-memory face/plate anonymization model fails or is unconfigured, the edge runtime automatically disables thumbnail generation and enforces strict metadata-only mode.
* **Encryption in Transit:** All client-to-server and edge-to-broker traffic is encrypted using modern TLS 1.3 cryptographic protocols with strong cipher suites.
* **Encryption at Rest:** Central PostgreSQL database volumes and Redis state stores utilize AES-256 block-level encryption.
* **Access Control & RBAC:** Access to the SentinelEdge web console requires Argon2id password-hashed authentication and JSON Web Tokens (JWT). Roles are segmented into `admin`, `operator`, and `viewer`.
* **Tamper-Evident Audit Trails:** Every operator action (acknowledging an incident, updating status, appending forensic notes) is logged in an immutable, timestamped audit log table in PostgreSQL.

---

## 6. Data Retention and Automated Purging

SentinelEdge enforces automatic metadata pruning:
* **Default Metadata Retention:** Incident logs, audit histories, and vector embeddings are retained for a configurable period (default: 30 days) before automated database vacuuming and archival.
* **Redis Streams Event Buffer:** Event queues in Redis operate as circular ring buffers with maximum event length limits (`MAXLEN 50000`), automatically dropping older processed events.
* **Immediate Edge Purge:** Edge video frames are discarded immediately after frame inference. No local disk buffers of unredacted video are maintained.

---

## 7. Data Subject Rights

Under GDPR Chapter III and California CCPA/CPRA, data subjects possess statutory rights. Because SentinelEdge does not store identifiable biometric profiles, requests are addressed as follows:
* **Right of Access & Portability:** Data subjects may request information regarding whether metadata alerts were triggered in specific monitored public zones during defined timeframes.
* **Right to Erasure (Right to be Forgotten):** Data Controllers can execute metadata purging for specific time intervals or zone identifiers directly via the SentinelEdge management API (`DELETE /api/v1/incidents/{id}`).
* **Right to Information:** Controllers must erect physical warning signage at physical boundaries declaring the presence of edge computer-vision sensors and referencing this Privacy Notice.

---

## 8. Incident Reporting and Data Breach Notification

In the event of an infrastructure compromise affecting central database records, the Data Controller must notify relevant supervisory authorities within 72 hours under GDPR Article 33. Because raw visual biometric data is never centralized, the risk of visual identity theft from database exfiltration is structurally mitigated by the SentinelEdge architecture.

---

## 9. Contact and Data Protection Officer Inquiries

For questions regarding the technological privacy controls of SentinelEdge, consult the engineering documentation or submit inquiries to the project repository:
* **Repository:** [https://github.com/BijoySarkar19/SentinelEdge](https://github.com/BijoySarkar19/SentinelEdge)
* **Architecture Documentation:** [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
* **GDPR Compliance Guide:** [docs/legal/GDPR_COMPLIANCE_GUIDE.md](GDPR_COMPLIANCE_GUIDE.md)
