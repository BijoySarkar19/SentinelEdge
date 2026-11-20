# SentinelEdge Deployment Guide

## Quick Start with Docker
```bash
# 1. Start backend infrastructure (PostgreSQL, Redis, Prometheus, Grafana)
docker compose up -d

# 2. Check container health
docker compose ps
```

## Native Edge CV Launch
```bash
# Native edge launch avoids container GPU virtualization overhead
python edge/src/sentinledge/main.py --source 0
```
