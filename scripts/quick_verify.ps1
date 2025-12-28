#!/usr/bin/env pwsh
# Pre-launch verification script
# Quick checks before starting the app

Write-Host "Checking system requirements..."

$checks_passed = 0
$checks_failed = 0

# Docker
if (docker --version 2>&1) {
    Write-Host "✅ Docker installed"
    $checks_passed++
} else {
    Write-Host "❌ Docker not installed"
    $checks_failed++
}

# Docker daemon
if (docker ps 2>&1 | Out-Null) {
    Write-Host "✅ Docker daemon running"
    $checks_passed++
} else {
    Write-Host "❌ Docker daemon not running"
    $checks_failed++
}

# Critical files
$files = @(
    "docker-compose.yml",
    "config.py",
    "utils/db_connection.py",
    "utils/database.py",
    "scripts/backup_database.ps1",
    "scripts/monitor_database.ps1"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists"
        $checks_passed++
    } else {
        Write-Host "❌ $file missing"
        $checks_failed++
    }
}

# Backup directory
if (Test-Path "postgres-backups") {
    Write-Host "✅ postgres-backups directory exists"
    $checks_passed++
} else {
    Write-Host "⚠️  postgres-backups directory does not exist (will create)"
    mkdir postgres-backups
}

Write-Host ""
Write-Host "Results: $checks_passed passed, $checks_failed failed"

if ($checks_failed -eq 0) {
    Write-Host "🎉 Ready to launch!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Fix issues above before launching" -ForegroundColor Red
    exit 1
}
