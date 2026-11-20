import uuid
import hashlib
from datetime import datetime, timezone
import httpx
import structlog
from sentinledge.rules.engine import RuleTriggerResult

logger = structlog.get_logger()

class EventProducer:
    def __init__(self, backend_url: str, ingest_endpoint: str = "/api/v1/incidents/ingest"):
        self.url = f"{backend_url.rstrip('/')}{ingest_endpoint}"
        self.client = httpx.Client(timeout=5.0)

    def send_incident_event(
        self,
        camera_id: str,
        rule_res: RuleTriggerResult,
        device: str,
        inference_latency_ms: float,
        privacy_status: dict,
        simulated: bool = False,
    ) -> bool:
        event_id = str(uuid.uuid4())
        raw_key = f"{camera_id}_{rule_res.rule_id}_{int(time.time() // 60)}"
        idempotency_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        payload = {
            "event_id": event_id,
            "idempotency_key": idempotency_key,
            "camera_id": camera_id,
            "rule_id": rule_res.rule_id,
            "event_type": rule_res.event_type,
            "severity": rule_res.severity,
            "confidence": rule_res.confidence,
            "summary": rule_res.summary,
            "object_counts": rule_res.object_counts,
            "detected_classes": rule_res.detected_classes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_device": device,
            "inference_backend": "yolo",
            "inference_latency_ms": round(inference_latency_ms, 2),
            "privacy_status": privacy_status,
            "simulated": simulated,
        }

        try:
            resp = self.client.post(self.url, json=payload)
            if resp.status_code in (200, 201):
                logger.info("Incident event dispatched to backend", event_id=event_id, type=rule_res.event_type)
                return True
            logger.warning("Backend returned non-200 for event ingest", status=resp.status_code, body=resp.text)
        except Exception as e:
            logger.error("Failed to post incident event", error=str(e), url=self.url)
        return False
