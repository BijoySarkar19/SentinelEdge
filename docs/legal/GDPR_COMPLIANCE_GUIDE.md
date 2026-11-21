# SentinelEdge GDPR Compliance Guide & DPIA Framework

**Standard Reference:** Regulation (EU) 2016/679 (General Data Protection Regulation)  
**Target Audience:** Data Protection Officers (DPOs), Corporate Legal Counsel, System Architects  
**Scope:** Edge Computer Vision, In-Memory Anonymization, and Central Metadata Storage

---

## 1. Executive Compliance Overview

Under the General Data Protection Regulation (GDPR), conventional Closed-Circuit Television (CCTV) systems present severe regulatory hurdles due to the indiscriminate collection and storage of high-resolution biometric imagery.

**SentinelEdge was engineered from the ground up to solve GDPR non-compliance:**

```
Traditional Cloud CCTV (High Risk)             SentinelEdge Architecture (Low Risk)
[ Camera ] ──(Raw Video)──> [ Cloud WAN ]      [ Camera ] ──> [ Edge Memory (RAM) ]
  • Continuous Facial PII Upload                 • Ephemeral Inference (30 ms)
  • Cloud Storage Vulnerability                  • In-Memory Face & Plate Blur
  • Huge Data Breach Impact                      • Zero Raw Video Leaves Edge
                                                 • Metadata-Only Event Dispatch
```

---

## 2. Article-by-Article GDPR Mapping

### Article 5: Principles Relating to Processing of Personal Data
* **Article 5(1)(a) — Lawfulness, Fairness, and Transparency:** SentinelEdge provides transparent audit logs of all detections and requires deployers to mount physical camera notice signage.
* **Article 5(1)(b) — Purpose Limitation:** Detections are triggered strictly for defined safety rules (e.g., restricted hazard zone intrusion). Data cannot be repurposed for generalized behavioral surveillance.
* **Article 5(1)(c) — Data Minimization:** The system enforces absolute minimization. Raw pixels are discarded immediately; only structured telemetry (timestamps, counts, bounding box coordinates) is retained.
* **Article 5(1)(e) — Storage Limitation:** Central metadata and vector embeddings are automatically pruned after a configurable retention window (default: 30 days).
* **Article 5(1)(f) — Integrity and Confidentiality:** Communications between edge nodes and the central console are encrypted via TLS 1.3. Stored database records are protected via AES-256 encryption.

### Article 9: Processing of Special Categories of Personal Data (Biometrics)
* **SentinelEdge Does Not Process Biometric Data for Identification:**
  Under GDPR Article 9, biometric data is subject to strict prohibitions if used *"for the purpose of uniquely identifying a natural person."*
  * ByteTrack assigns temporary integer tracking tokens (e.g., `104`) solely to compute dwell duration.
  * No facial embeddings, facial geometry measurements, or biometric vectors are generated or cross-referenced.
  * Therefore, SentinelEdge does **not** fall under Article 9 special category restrictions.

### Article 25: Data Protection by Design and by Default
* **Privacy by Design:** Privacy is not an optional add-on; it is hardcoded into the data flow. The edge pipeline explicitly executes the anonymization filter *before* any optional preview thumbnail can be written.
* **Fail-Safe Mechanism:** If the face blur filter fails, image capture is locked down automatically, defaulting to metadata-only transmission.

### Article 32: Security of Processing
* Central REST APIs require Argon2id password-derived JWT tokens.
* Database connections utilize parameterized asyncpg queries preventing SQL injection.
* Network edge nodes communicate over an isolated subnetwork or VPN.

---

## 3. Data Protection Impact Assessment (DPIA) Framework (Article 35)

When deploying SentinelEdge in public or commercial facilities, organizations should document their DPIA using this structured framework:

### Step 1: Systematic Description of the Processing
* **System Component:** Edge device running YOLOv8n object detection and ByteTrack association.
* **Input Data:** Real-time RTSP video stream from facility cameras.
* **Processing Location:** Edge device volatile RAM (no disk recording).
* **Transmitted Output:** Non-PII incident event payloads via Redis Streams to central PostgreSQL instance.

### Step 2: Assessment of Necessity and Proportionality
* **Legitimate Interest:** Preventing unauthorized perimeter access, ensuring chemical storage safety, and maintaining clear fire egress routes.
* **Proportionality Test:** Why not traditional video recording? SentinelEdge is **more proportional and less intrusive** than traditional CCTV because it does not record or store raw video of innocent bystanders.

### Step 3: Assessment of Risks to the Rights of Data Subjects
| Potential Risk | Severity | Mitigating SentinelEdge Measure |
| :--- | :--- | :--- |
| Exfiltration of video database | Low | Impossible: No central video database exists. |
| Identification of individuals | Negligible | In-memory Gaussian blur obscures facial features. |
| Function creep (tracking employees) | Low | Ephemeral track IDs reset when leaving camera FOV. |
| Operator abuse | Low | Every status update and note is logged in `incident_audits`. |

### Step 4: Measures Envisaged to Address Risks
1. Deploy physical warning notices with QR code linking to the Controller's Privacy Policy.
2. Restrict console access to authorized security operators via RBAC.
3. Schedule automatic database pruning to enforce strict storage limitation.

---

## 4. International Data Transfers (Chapter V)

Because SentinelEdge can be deployed 100% on-premise or in sovereign local edge clusters:
* **Zero Cross-Border Video Data Transfers:** Video streams remain localized to the physical facility.
* **Sovereignty Compliance:** Deployments in the European Union retain all incident telemetry within EU boundaries, eliminating US CLOUD Act or standard contractual clause (SCC) transfer complications.
