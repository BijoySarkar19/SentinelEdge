# SentinelEdge Production Deployment Guide & Runbook

This guide covers deploying **SentinelEdge** into enterprise-grade production environments (AWS, GCP, Azure, bare-metal clusters, or edge server appliances).

---

## 1. Production Architecture Topology

```
               [ HTTPS / WSS: Port 443 / 80 ]
                            │
               ┌────────────▼────────────┐
               │    NGINX EDGE GATEWAY    │
               │  (SSL, Rate Limit, Gzip)│
               └──────┬────────────┬─────┘
                      │            │
       [ /api, /ws ]  │            │  [ /, /_next ]
                      │            │
         ┌────────────▼──┐       ┌─▼──────────────────┐
         │ FastAPI REST  │       │ Next.js 15 Console │
         │   (4 Workers) │       │ (Standalone Node)  │
         └───────┬───────┘       └────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼──────────┐   ┌──────▼─────────┐
│ PostgreSQL 16  │   │   Redis 7.4    │
│  + pgvector    │   │ (Event Streams)│
└────────────────┘   └───────▲────────┘
                             │
                     ┌───────┴────────┐
                     │ YOLOv8 Edge CV │
                     │   (GPU/CPU)    │
                     └────────────────┘
```

---

## 2. Hardware Sizing & Prerequisites

| Component | Minimum Production Spec | Recommended Enterprise Spec |
| :--- | :--- | :--- |
| **CPU** | 4 Cores (x86_64 or aarch64) | 8–16 Cores |
| **RAM** | 8 GB | 16–32 GB |
| **Storage** | 100 GB NVMe SSD | 500 GB NVMe SSD (RAID-1/10) |
| **GPU (Edge Node)** | NVIDIA RTX 3050 (4GB+) / T4 | NVIDIA RTX 4090 / A10G / L4 |
| **OS** | Ubuntu 22.04 LTS / Debian 12 | Ubuntu 24.04 LTS / RHEL 9 |
| **Docker** | Docker Engine 24.0+ | Docker Engine 27.0+ with Compose v2 |

---

## 3. Quickstart: One-Command Deployment

### Linux / macOS
```bash
cd SentinelEdge

# 1. Prepare production environment
cp .env.production.example .env.production
nano .env.production  # Set real database passwords & JWT secret

# 2. Execute deployment
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Windows Server / PowerShell
```powershell
cd SentinelEdge

# 1. Prepare production environment
Copy-Item .env.production.example .env.production
notepad .env.production

# 2. Execute deployment
.\scripts\deploy.ps1
```

---

## 4. Domain & SSL/TLS Configuration

Place your TLS certificate and private key inside `infrastructure/nginx/ssl`:

```bash
mkdir -p infrastructure/nginx/ssl
cp /etc/letsencrypt/live/sentinel.yourdomain.com/fullchain.pem infrastructure/nginx/ssl/sentinel.crt
cp /etc/letsencrypt/live/sentinel.yourdomain.com/privkey.pem infrastructure/nginx/ssl/sentinel.key
```

Update `infrastructure/nginx/nginx.conf` server block to enable HTTPS:

```nginx
server {
    listen 443 ssl http2;
    server_name sentinel.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/sentinel.crt;
    ssl_certificate_key /etc/nginx/ssl/sentinel.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ...
}
```

---

## 5. Automated Backup & Disaster Recovery

### Automated PostgreSQL (with pgvector) Backup:
Add this cron job (`crontab -e`) to backup vector embeddings and incident logs nightly:

```bash
0 2 * * * docker compose -f /opt/sentinel/compose.prod.yaml exec -T postgres pg_dump -U sentinel_prod sentineledge_prod | gzip > /opt/backups/sentinel_db_$(date +\%F).sql.gz
```

### Restore Database from Backup:
```bash
gunzip < /opt/backups/sentinel_db_2026-11-20.sql.gz | docker compose -f compose.prod.yaml exec -T postgres psql -U sentinel_prod sentineledge_prod
```

---

## 6. Horizontal Scaling Strategy

1. **Backend Web Workers**: In `.env.production`, adjust `BACKEND_WORKERS=8` for multi-core CPUs.
2. **Distributed Camera Ingestion**: Edge processing containers can be deployed across multiple physical cameras or micro-appliances (e.g. Jetson Orin Nano / RTX Edge PCs), pushing metadata payloads into central Redis Streams or the `/api/v1/incidents/ingest` endpoint.
3. **Zero-Video WAN Guarantee**: Raw video is strictly kept within local edge RAM/VRAM buffers. Only structured metadata and optional anonymized crops are transmitted over WAN.

---

## 7. Security Hardening Checklist

- [x] **Non-Root Containers**: Backend runs as `sentinel` (uid 1001), frontend runs as `nextjs` (uid 1001).
- [x] **Rate Limiting**: Nginx gates auth requests at 5 requests/sec and API at 30 requests/sec.
- [x] **Security Headers**: HSTS, CSP, X-Frame-Options (`SAMEORIGIN`), X-Content-Type-Options (`nosniff`).
- [x] **JWT & Password Security**: Argon2id password hashing with salts; signed HS256 JWT access tokens.
- [x] **Database Isolation**: PostgreSQL and Redis run on an isolated internal bridge network (`sentinel_prod_net`) not exposed to public WAN.
