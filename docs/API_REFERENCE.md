# SentinelEdge REST API Reference (v1)

Base URL: `/api/v1`

## Key Endpoints

- `POST /api/v1/auth/login`: Authenticate operator and set HTTP-only cookie.
- `GET /api/v1/cameras`: List all monitored camera nodes.
- `POST /api/v1/incidents/ingest`: Edge node event ingestion endpoint with idempotency.
- `GET /api/v1/incidents`: Retrieve paginated incidents with status and severity filters.
- `POST /api/v1/incidents/{id}/acknowledge`: Mark incident acknowledged by human operator.
- `POST /api/v1/incidents/{id}/resolve`: Resolve incident with resolution comment.
- `POST /api/v1/search/semantic`: Natural language incident search powered by pgvector.
- `GET /api/v1/analytics/summary`: Real-time KPI metrics.
- `GET /api/v1/health/ready`: Subsystem readiness probe.
