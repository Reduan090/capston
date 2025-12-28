# scripts/monitor_database.ps1
# REAL-TIME DATABASE MONITORING SCRIPT
# Monitors PostgreSQL health, performance, and connection status

param(
    [int]$Interval = 5,  # Check every 5 seconds
    [string]$LogFile = "logs\database_monitor.log"
)

# Ensure log directory exists
$LogDir = Split-Path -Path $LogFile
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    Write-Host $LogMessage
}

function Check-Database {
    try {
        # Try to connect to database
        $Output = docker exec capstone-postgres pg_isready -U capstone 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            return @{
                Status = "HEALTHY"
                Message = "Database is accepting connections"
                Timestamp = Get-Date
            }
        } else {
            return @{
                Status = "UNHEALTHY"
                Message = "Database is rejecting connections"
                Timestamp = Get-Date
            }
        }
    } catch {
        return @{
            Status = "UNREACHABLE"
            Message = "Cannot reach Docker container"
            Error = $_.Exception.Message
            Timestamp = Get-Date
        }
    }
}

function Check-ContainerStatus {
    try {
        $Info = docker inspect capstone-postgres 2>&1 | ConvertFrom-Json
        return @{
            State = $Info[0].State.Status
            Running = $Info[0].State.Running
            RestartCount = $Info[0].RestartCount
            Timestamp = Get-Date
        }
    } catch {
        return @{
            State = "UNKNOWN"
            Error = $_.Exception.Message
            Timestamp = Get-Date
        }
    }
}

function Check-DiskSpace {
    $Drive = (Get-Item "postgres-data").PSDrive
    $Volume = Get-Volume -DriveLetter $Drive.Name
    
    return @{
        DriveLetter = $Drive.Name
        TotalGB = [math]::Round($Volume.Size / 1GB, 2)
        FreeGB = [math]::Round($Volume.SizeRemaining / 1GB, 2)
        UsedPercent = [math]::Round((($Volume.Size - $Volume.SizeRemaining) / $Volume.Size) * 100, 2)
    }
}

# Main monitoring loop
Write-Host "🚀 Starting Database Monitor..." -ForegroundColor Cyan
Log "Database monitoring started"

$CheckCount = 0

while ($true) {
    $CheckCount++
    Clear-Host
    
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║      PostgreSQL PRODUCTION MONITORING DASHBOARD        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    Write-Host "`n📊 Check #$CheckCount | $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
    
    # Database Status
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🗄️  DATABASE STATUS" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $DbCheck = Check-Database
    $StatusColor = if ($DbCheck.Status -eq "HEALTHY") { "Green" } else { "Red" }
    Write-Host "  Status: " -NoNewline
    Write-Host $DbCheck.Status -ForegroundColor $StatusColor
    Write-Host "  Message: $($DbCheck.Message)"
    
    # Container Status
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🐳 CONTAINER STATUS" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $ContainerStatus = Check-ContainerStatus
    $RunColor = if ($ContainerStatus.Running) { "Green" } else { "Red" }
    Write-Host "  Container State: $($ContainerStatus.State)" -ForegroundColor $RunColor
    Write-Host "  Running: $($ContainerStatus.Running)"
    Write-Host "  Restarts: $($ContainerStatus.RestartCount)"
    
    # Disk Space
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "💾 DISK SPACE" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $DiskStatus = Check-DiskSpace
    $DiskColor = if ($DiskStatus.UsedPercent -gt 80) { "Red" } else { "Green" }
    Write-Host "  Drive: $($DiskStatus.DriveLetter):"
    Write-Host "  Total: $($DiskStatus.TotalGB) GB"
    Write-Host "  Free: $($DiskStatus.FreeGB) GB" -ForegroundColor $DiskColor
    Write-Host "  Used: $($DiskStatus.UsedPercent)%" -ForegroundColor $DiskColor
    
    # Commands
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "⌨️  COMMANDS" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "  [B] Backup Database"
    Write-Host "  [L] View Logs"
    Write-Host "  [R] Restart Container"
    Write-Host "  [S] Stop Monitoring"
    Write-Host ""
    
    # Log the status
    Log "Health Check - Database: $($DbCheck.Status), Container: $($ContainerStatus.State), Disk Used: $($DiskStatus.UsedPercent)%"
    
    # Wait for interval or user input
    $Key = [Console]::ReadKey($true)
    if ($Key.KeyChar -eq 'q' -or $Key.KeyChar -eq 'S') {
        break
    } elseif ($Key.KeyChar -eq 'b' -or $Key.KeyChar -eq 'B') {
        Write-Host "`n🔄 Starting backup..." -ForegroundColor Cyan
        & ".\scripts\backup_database.ps1"
    } elseif ($Key.KeyChar -eq 'l' -or $Key.KeyChar -eq 'L') {
        Get-Content $LogFile -Tail 20
    } elseif ($Key.KeyChar -eq 'r' -or $Key.KeyChar -eq 'R') {
        Write-Host "`n⏸️  Restarting container..." -ForegroundColor Yellow
        docker restart capstone-postgres
    }
    
    Start-Sleep -Seconds $Interval
}

Log "Database monitoring stopped"
Write-Host "`n✅ Monitor stopped" -ForegroundColor Green
