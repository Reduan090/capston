#!/usr/bin/env pwsh
# Capstone Research Assistant - Quick Start Script
# Usage: .\start.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Capstone Research Assistant - Startup Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "  ✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker not running. Starting Docker Desktop..." -ForegroundColor Red
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "  Waiting 20 seconds for Docker to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
}

# Start PostgreSQL
Write-Host ""
Write-Host "[2/4] Starting PostgreSQL database..." -ForegroundColor Yellow
docker-compose up -d
Start-Sleep -Seconds 3

$containerStatus = docker ps --filter "name=capstone-postgres" --format "{{.Status}}"
if ($containerStatus -match "Up") {
    Write-Host "  ✓ PostgreSQL container running" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to start PostgreSQL" -ForegroundColor Red
    exit 1
}

# Check migrations
Write-Host ""
Write-Host "[3/4] Checking database migrations..." -ForegroundColor Yellow
$migrationStatus = & "C:/Projects/capstone/venv/Scripts/python.exe" scripts/migrate_db.py status 2>&1 | Select-String "Current Version:"
if ($migrationStatus -match "Current Version: 0") {
    Write-Host "  ⚠ No migrations applied. Running migrations..." -ForegroundColor Yellow
    & "C:/Projects/capstone/venv/Scripts/python.exe" scripts/migrate_db.py migrate
    Write-Host "  ✓ Migrations applied" -ForegroundColor Green
} else {
    Write-Host "  ✓ Database schema up to date" -ForegroundColor Green
}

# Launch application
Write-Host ""
Write-Host "[4/4] Launching Streamlit application..." -ForegroundColor Yellow
Write-Host "  → Opening browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Demo Credentials:" -ForegroundColor Cyan
Write-Host "  Username: demo       | Password: Demo123456" -ForegroundColor White
Write-Host "  Username: researcher | Password: Research123" -ForegroundColor White
Write-Host "  Username: student    | Password: Student123" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

& "C:/Projects/capstone/venv/Scripts/streamlit.exe" run app.py
