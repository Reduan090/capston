# AUTOMATED DATABASE BACKUP SCRIPT
# Runs daily backups to ensure data recovery capability
# Usage: ./scripts/backup_database.ps1

param(
    [string]$BackupDir = "postgres-backups"
)

# Configuration
$DB_USER = "capstone"
$DB_HOST = "localhost"
$DB_PORT = "5433"
$DB_NAME = "capstone_db"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd_HHmmss"
$BACKUP_FILE = "$BackupDir\capstone_db_backup_$TIMESTAMP.sql"
$LOG_FILE = "$BackupDir\backup_$TIMESTAMP.log"

Write-Host "🔄 Starting PostgreSQL backup..." -ForegroundColor Cyan

# Create backup directory if not exists
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "✅ Created backup directory: $BackupDir"
}

try {
    # Perform backup using pg_dump inside Docker container
    Write-Host "📦 Dumping database from Docker container..."
    
    docker exec capstone-postgres pg_dump `
        -U $DB_USER `
        -h localhost `
        -p 5432 `
        -d $DB_NAME `
        -F c `
        -v `
        -f /var/backups/postgres/backup.dump 2>&1 | Tee-Object -FilePath $LOG_FILE
    
    # Copy backup from container to host
    docker cp capstone-postgres:/var/backups/postgres/backup.dump $BACKUP_FILE
    
    # Get backup file size
    $BackupSize = (Get-Item $BACKUP_FILE).Length / 1MB
    
    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host "📁 Backup file: $BACKUP_FILE"
    Write-Host "💾 Size: $([math]::Round($BackupSize, 2)) MB"
    
    # Keep only last 7 backups (weekly retention)
    Write-Host "🧹 Cleaning old backups (keeping 7 most recent)..."
    Get-ChildItem -Path $BackupDir -Filter "capstone_db_backup_*.dump" | 
        Sort-Object CreationTime -Descending | 
        Select-Object -Skip 7 | 
        Remove-Item
    
    Write-Host "✅ Cleanup completed"
    
} catch {
    Write-Host "❌ Backup failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Backup process finished" -ForegroundColor Green
