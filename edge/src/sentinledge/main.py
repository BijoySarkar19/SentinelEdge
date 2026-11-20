import sys
import time
import structlog
from config.settings import edge_settings
from sentinledge.utils.gpu_diagnostics import print_diagnostic_banner, run_gpu_diagnostic
from sentinledge.ingestion.video_reader import VideoIngestionSource
from sentinledge.detection.yolo_detector import YOLOv8Detector
from sentinledge.tracking.bytetrack import MultiObjectTracker
from sentinledge.privacy.privacy_filter import PrivacyPipeline
from sentinledge.rules.engine import RulesEngine, RuleDefinition
from sentinledge.events.producer import EventProducer
from sentinledge.performance.metrics import PerformanceMonitor

logger = structlog.get_logger()

def main():
    print_diagnostic_banner()
    diag = run_gpu_diagnostic()

    device = "cuda" if diag["cuda_available"] and edge_settings.inference_device != "cpu" else "cpu"
    logger.info("Initializing SentinelEdge CV Pipeline", device=device, camera=edge_settings.camera_id)

    # Initialize components
    detector = YOLOv8Detector(
        device=device,
        conf_threshold=edge_settings.inference_confidence,
        img_size=edge_settings.inference_image_size,
        fp16=edge_settings.inference_fp16,
    )
    detector.load()

    tracker = MultiObjectTracker()
    privacy = PrivacyPipeline(mode=edge_settings.privacy_mode)
    rules = RulesEngine([
        RuleDefinition(
            rule_id="RULE-CROWD-01",
            rule_name="Unusual Crowd Density",
            rule_type="crowd_density",
            camera_id=edge_settings.camera_id,
            zone_id=None,
            threshold_count=5,
            duration_seconds=3.0,
            severity="high",
            cooldown_seconds=30.0,
        ),
        RuleDefinition(
            rule_id="RULE-RESTRICTED-01",
            rule_name="Restricted Zone Breach",
            rule_type="restricted_zone",
            camera_id=edge_settings.camera_id,
            zone_id=None,
            threshold_count=1,
            duration_seconds=2.0,
            severity="critical",
            cooldown_seconds=30.0,
        ),
        RuleDefinition(
            rule_id="RULE-VEHICLE-01",
            rule_name="Vehicle Congestion Check",
            rule_type="vehicle_congestion",
            camera_id=edge_settings.camera_id,
            zone_id=None,
            threshold_count=3,
            duration_seconds=5.0,
            severity="medium",
            cooldown_seconds=45.0,
        ),
    ])
    producer = EventProducer(backend_url=edge_settings.backend_api_url, ingest_endpoint=edge_settings.ingest_endpoint)
    monitor = PerformanceMonitor()

    # Video Source
    source = VideoIngestionSource(edge_settings.source_uri, frame_skip=edge_settings.inference_frame_skip)
    logger.info("Opening video source", source=edge_settings.source_uri)
    if not source.open():
        logger.warning("Could not open video source; running dry pipeline test loop with synthetic stream", source=edge_settings.source_uri)
        import numpy as np
        fake_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        def _synthetic_stream():
            idx = 0
            while True:
                idx += 1
                time.sleep(0.1)
                yield idx, time.time(), fake_frame.copy()
        frames_gen = _synthetic_stream()
    else:
        frames_gen = source.frames()

    logger.info("SentinelEdge Edge Pipeline Active and Running.")
    try:
        for frame_id, ts, frame in frames_gen:
            t0 = time.perf_counter()
            detections = detector.detect(frame)
            inf_ms = (time.perf_counter() - t0) * 1000.0

            tracks = tracker.update(detections, ts)
            _, privacy_stats = privacy.process(frame)
            triggers = rules.evaluate(tracks, ts)

            for trig in triggers:
                producer.send_incident_event(
                    camera_id=edge_settings.camera_id,
                    rule_res=trig,
                    device=device,
                    inference_latency_ms=inf_ms,
                    privacy_status=privacy_stats,
                    simulated=False,
                )

            monitor.record_frame(inf_ms)
            if frame_id % 30 == 0:
                logger.info(
                    "Telemetry",
                    frame=frame_id,
                    fps=monitor.fps,
                    latency_ms=monitor.avg_latency_ms,
                    active_tracks=len(tracks),
                )
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
    finally:
        source.close()

if __name__ == "__main__":
    main()
