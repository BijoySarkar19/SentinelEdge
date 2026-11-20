from prometheus_client import Counter, Histogram, Gauge

# Computer vision edge metrics
EDGE_FRAMES_PROCESSED = Counter(
    "sentinel_edge_frames_total",
    "Total video frames processed by edge runtime",
    ["camera_id", "device"]
)

EDGE_INFERENCE_LATENCY = Histogram(
    "sentinel_edge_inference_latency_seconds",
    "Inference execution time in seconds",
    ["model", "device"],
    buckets=[0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0]
)

EDGE_PRIVACY_FILTER_LATENCY = Histogram(
    "sentinel_edge_privacy_filter_latency_seconds",
    "Time taken to detect and anonymize faces/plates",
    buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
)

# Backend ingestion metrics
INGESTED_EVENTS_TOTAL = Counter(
    "sentinel_ingested_events_total",
    "Total detection and incident events ingested",
    ["event_type", "severity", "simulated"]
)

ACTIVE_WEBSOCKET_CONNECTIONS = Gauge(
    "sentinel_active_websocket_connections",
    "Number of active WebSocket connections to the incident feed"
)

# Semantic search metrics
SEARCH_LATENCY = Histogram(
    "sentinel_semantic_search_latency_seconds",
    "Search execution latency for semantic pgvector retrieval",
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
)
