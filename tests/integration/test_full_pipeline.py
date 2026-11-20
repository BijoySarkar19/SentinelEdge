import pytest

def test_full_pipeline_contract():
    """Verify that edge event contracts align with backend ingestion expectations."""
    from app.schemas.events import EdgeEventPayload
    
    sample_event = {
        "event_id": "test-e2e-01",
        "idempotency_key": "idemp-01",
        "camera_id": "CAM-01",
        "event_type": "crowd_density",
        "severity": "high",
        "confidence": 0.95,
        "summary": "Crowd density breach",
        "timestamp": "2026-11-20T12:00:00Z",
        "simulated": True,
    }
    obj = EdgeEventPayload(**sample_event)
    assert obj.event_id == "test-e2e-01"
    assert obj.simulated is True
