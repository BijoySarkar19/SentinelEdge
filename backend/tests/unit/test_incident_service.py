import pytest
from app.schemas.events import EdgeEventPayload

def test_edge_event_schema_validation():
    valid_data = {
        "event_id": "evt-1234",
        "idempotency_key": "idemp-5678",
        "camera_id": "cam-01",
        "event_type": "crowd_density",
        "severity": "high",
        "confidence": 0.92,
        "summary": "High crowd density detected in zone A",
        "timestamp": "2026-11-20T12:00:00Z",
    }
    payload = EdgeEventPayload(**valid_data)
    assert payload.event_id == "evt-1234"
    assert payload.severity == "high"
    assert payload.simulated is False

def test_edge_event_schema_invalid_severity():
    invalid_data = {
        "event_id": "evt-1234",
        "idempotency_key": "idemp-5678",
        "camera_id": "cam-01",
        "event_type": "crowd_density",
        "severity": "extreme",  # Not in allowed enum
        "confidence": 0.92,
        "summary": "Invalid severity",
        "timestamp": "2026-11-20T12:00:00Z",
    }
    with pytest.raises(Exception):
        EdgeEventPayload(**invalid_data)
