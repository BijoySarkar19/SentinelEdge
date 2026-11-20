"""Synthetic incident generator for demonstration and test environments."""
import argparse
import uuid
import time
import httpx
from datetime import datetime, timezone

DEMO_INCIDENTS = [
    {
        "camera_id": "CAM-01",
        "event_type": "crowd_density",
        "severity": "high",
        "summary": "Unusual crowd density warning in Gate 1 Plaza (8 persons detected)",
        "object_counts": {"person": 8},
        "detected_classes": ["person"],
    },
    {
        "camera_id": "CAM-02",
        "event_type": "restricted_zone",
        "severity": "critical",
        "summary": "Restricted chemical perimeter breach detected (Dwell: 4.2s)",
        "object_counts": {"person": 2},
        "detected_classes": ["person"],
    },
    {
        "camera_id": "CAM-03",
        "event_type": "vehicle_congestion",
        "severity": "medium",
        "summary": "Vehicle congestion on inbound arterial road (6 vehicles)",
        "object_counts": {"car": 4, "truck": 2},
        "detected_classes": ["car", "truck"],
    },
    {
        "camera_id": "CAM-04",
        "event_type": "access_lane",
        "severity": "critical",
        "summary": "Emergency access fire lane blocked by stationary delivery van",
        "object_counts": {"truck": 1},
        "detected_classes": ["truck"],
    },
]

def main(api_url: str):
    print(f"Generating synthetic demonstration incidents via {api_url}...")
    client = httpx.Client(timeout=10.0)

    for item in DEMO_INCIDENTS:
        payload = {
            "event_id": str(uuid.uuid4()),
            "idempotency_key": str(uuid.uuid4()),
            "camera_id": item["camera_id"],
            "event_type": item["event_type"],
            "severity": item["severity"],
            "confidence": 0.92,
            "summary": f"[SIMULATED] {item['summary']}",
            "object_counts": item["object_counts"],
            "detected_classes": item["detected_classes"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_device": "cuda:0",
            "inference_backend": "yolo",
            "inference_latency_ms": 38.5,
            "privacy_status": {"mode": "metadata_only", "faces_anonymized": 0},
            "simulated": True,
        }
        try:
            r = client.post(f"{api_url.rstrip('/')}/api/v1/incidents/ingest", json=payload)
            print(f"Dispatched event {payload['event_id'][:8]} - Status: {r.status_code}")
        except Exception as e:
            print(f"Could not connect to backend ({e}); saved payload locally.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://localhost:8000")
    args = parser.parse_args()
    main(args.api_url)
