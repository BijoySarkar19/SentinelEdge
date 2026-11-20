# =============================================================================
# SentinelEdge — Automated Production Deployment Script (PowerShell)
# Supports: Windows Server 2022 / Windows 11 Enterprise / WSL2
# =============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   SentinelEdge Production Deployment Engine (PowerShell)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

Set-Location $RootDir

# 1. Sanity check prerequisites
Write-Host "[1/6] Validating deployment prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "docker is required but not installed. Aborting."
}

# 2. Check environment file
Write-Host "[2/6] Checking production environment file..." -ForegroundColor Yellow
if (-not (Test-Path ".env.production")) {
    if (Test-Path ".env") {
        Write-Host "Note: .env.production not found; copying active .env." -ForegroundColor Gray
        Copy-Item ".env" ".env.production"
    } else {
        Write-Host "Creating .env.production from .env.production.example..." -ForegroundColor Gray
        Copy-Item ".env.production.example" ".env.production"
    }
}

# 3. Build production images
Write-Host "[3/6] Building production container images..." -ForegroundColor Yellow
docker compose -f compose.prod.yaml build

# 4. Launch database and broker
Write-Host "[4/6] Bootstrapping PostgreSQL (pgvector) and Redis..." -ForegroundColor Yellow
docker compose -f compose.prod.yaml up -d postgres redis
Start-Sleep -Seconds 8

# 5. Launch remaining services
Write-Host "[5/6] Starting application services (Backend, Frontend, Edge, Gateway, Observability)..." -ForegroundColor Yellow
docker compose -f compose.prod.yaml up -d

# 6. Verify health
Write-Host "[6/6] Verifying service statuses..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
docker compose -f compose.prod.yaml ps

Write-Host "=================================================================" -ForegroundColor Green
Write-Host "   SentinelEdge Production Deployment Ready!" -ForegroundColor Green
Write-Host "   Console UI:    http://localhost" -ForegroundColor Green
Write-Host "   REST Docs:     http://localhost/api/docs" -ForegroundColor Green
Write-Host "   Health Check:  http://localhost/health" -ForegroundColor Green
Write-Host "   Grafana:       http://localhost:3001" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
