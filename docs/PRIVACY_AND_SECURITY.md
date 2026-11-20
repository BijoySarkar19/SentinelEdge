# SentinelEdge Privacy & Security Architecture

## Core Architectural Guarantees

1. **Edge-Constrained Visual Data**:
   Video frames remain exclusively in temporary RAM on the edge processing device. No raw footage is transmitted to the central server or stored on disk by default.

2. **Automated Anonymization**:
   Faces and license plates are detected and blurred in memory prior to generating any optional preview thumbnails.

3. **No Biometric Identification**:
   Tracking IDs (e.g., Track-104) are ephemeral sequence numbers used exclusively for dwell-time and count calculation. The system performs NO facial recognition, emotion analysis, or demographic categorization.

4. **Fail-Safe Privacy Protection**:
   If an anonymization model fails or is unconfigured, the pipeline automatically locks down image output and switches to strict metadata-only mode.
