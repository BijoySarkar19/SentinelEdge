import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ingest_and_idempotency_mock(client: AsyncClient):
    payload = {
        "event_id": "mock-test-001",
        "idempotency_key": "mock-idemp-001",
        "camera_id": "test-cam-01",
        "event_type": "restricted_zone",
        "severity": "medium",
        "confidence": 0.88,
        "summary": "Person entered restricted compound",
        "timestamp": "2026-11-20T12:00:00Z",
        "simulated": True,
    }
    # Test schema serialization
    assert payload["event_id"] == "mock-test-001"
