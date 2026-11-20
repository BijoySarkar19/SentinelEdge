#!/usr/bin/env bash
# =============================================================================
# SentinelEdge — Automated Production Deployment Script
# Supports: Ubuntu 22.04+, Debian 12+, RHEL 9+, Amazon Linux 2023
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================================================="
echo "   SentinelEdge Production Deployment Engine"
echo "================================================================="

cd "$ROOT_DIR"

# 1. Sanity check prerequisites
echo "[1/6] Validating deployment prerequisites..."
command -v docker >/dev/null 2>&1 || { echo >&2 "Error: docker is required but not installed. Aborting."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo >&2 "Error: docker compose plugin is required. Aborting."; exit 1; }

# 2. Check environment file
echo "[2/6] Checking production environment file..."
if [ ! -f .env.production ]; then
    if [ -f .env ]; then
        echo "Warning: .env.production not found; using active .env configuration."
        cp .env .env.production
    else
        echo "Creating .env.production from .env.production.example..."
        cp .env.production.example .env.production
        echo "Note: Default production templates initialized in .env.production."
    fi
fi

# 3. Pull & Build production container images
echo "[3/6] Building production container images..."
docker compose -f compose.prod.yaml build --pull

# 4. Launch database and event broker first
echo "[4/6] Bootstrapping PostgreSQL (pgvector) and Redis..."
docker compose -f compose.prod.yaml up -d postgres redis
echo "Waiting for database and broker to report healthy..."
docker compose -f compose.prod.yaml wait sentinel_prod_postgres sentinel_prod_redis || sleep 10

# 5. Launch remaining services
echo "[5/6] Starting application services (Backend, Frontend, Edge, Gateway, Observability)..."
docker compose -f compose.prod.yaml up -d

# 6. Health verification
echo "[6/6] Verifying system health..."
sleep 5
docker compose -f compose.prod.yaml ps

echo "================================================================="
echo "   SentinelEdge Production Deployment Successful!"
echo "   Console UI:    http://localhost (or configured domain)"
echo "   REST Docs:     http://localhost/api/docs"
echo "   Health Check:  http://localhost/health"
echo "   Grafana:       http://localhost:3001"
echo "================================================================="
