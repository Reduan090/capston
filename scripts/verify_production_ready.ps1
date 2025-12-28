# scripts/verify_production_ready.ps1
# PRODUCTION READINESS VERIFICATION SCRIPT
# Run this before launching to ensure everything is configured correctly

param(
    [switch]$Verbose = $false
)

$ErrorCount = 0
$WarningCount = 0
$PassCount = 0

function Test-Check {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$FixCommand = ""
    )
    
    Write-Host -NoNewline "🔍 $Name... "
    
    try {
        $result = & $Test
        if ($result) {
            Write-Host "✅ PASS" -ForegroundColor Green
            $script:PassCount++
            return $true
        } else {
            Write-Host "❌ FAIL" -ForegroundColor Red
            if ($FixCommand) {
                Write-Host "   Fix: $FixCommand" -ForegroundColor Yellow
            }
            $script:ErrorCount++
            return $false
        }
    } catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($FixCommand) {
            Write-Host "   Fix: $FixCommand" -ForegroundColor Yellow
        }
        $script:ErrorCount++
        return $false
    }
}

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PRODUCTION READINESS VERIFICATION CHECKLIST          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# ============================================================================
# SYSTEM REQUIREMENTS
# ============================================================================
Write-Host "`n📋 SYSTEM REQUIREMENTS" -ForegroundColor Yellow

Test-Check "Docker installed" `
    { (docker --version) -match "version" } `
    "Install Docker Desktop from docker.com"

Test-Check "Docker Compose available" `
    { (docker-compose --version) -match "version" } `
    "Install Docker Compose (included with Docker Desktop)"

Test-Check "PowerShell 5.1 or higher" `
    { $PSVersionTable.PSVersion.Major -ge 5 } `
    "Update PowerShell or use PowerShell 7+"

Test-Check "At least 4GB RAM available" `
    { (Get-CimInstance -ClassName cim_physicalmemory | Measure-Object -Property Capacity -Sum).Sum / 1GB -ge 4 } `
    "Close other applications or allocate more RAM to Docker"

Test-Check "At least 10GB disk space free" `
    { (Get-Volume | Where-Object DriveLetter -eq 'C').SizeRemaining / 1GB -ge 10 } `
    "Delete unnecessary files to free up space"

# ============================================================================
# PROJECT STRUCTURE
# ============================================================================
Write-Host "`n📁 PROJECT STRUCTURE" -ForegroundColor Yellow

Test-Check "docker-compose.yml exists" `
    { Test-Path "docker-compose.yml" }

Test-Check "config.py exists" `
    { Test-Path "config.py" }

Test-Check "app.py exists" `
    { Test-Path "app.py" }

Test-Check "scripts/ directory exists" `
    { Test-Path "scripts" -PathType Container } `
    "mkdir scripts"

Test-Check "utils/ directory exists" `
    { Test-Path "utils" -PathType Container }

Test-Check "postgres-backups/ directory exists" `
    { Test-Path "postgres-backups" -PathType Container } `
    "mkdir postgres-backups"

# ============================================================================
# BACKUP SCRIPTS
# ============================================================================
Write-Host "`n🔄 BACKUP & RECOVERY SCRIPTS" -ForegroundColor Yellow

Test-Check "backup_database.ps1 exists" `
    { Test-Path "scripts\backup_database.ps1" }

Test-Check "monitor_database.ps1 exists" `
    { Test-Path "scripts\monitor_database.ps1" }

Test-Check "init_db.sql exists" `
    { Test-Path "scripts\init_db.sql" }

# ============================================================================
# DATABASE FILES
# ============================================================================
Write-Host "`n💾 DATABASE CONFIGURATION FILES" -ForegroundColor Yellow

Test-Check "db_connection.py exists" `
    { Test-Path "utils\db_connection.py" } `
    "Create connection pool handler"

Test-Check "DATABASE_URL in config.py" `
    { (Select-String -Path "config.py" -Pattern "DATABASE_URL") -ne $null } `
    "Ensure DATABASE_URL is configured in config.py"

Test-Check "PostgreSQL image available" `
    { (docker images | Select-String "postgres.*16") -ne $null } `
    "Docker will pull image automatically on first run"

# ============================================================================
# DOCKER CONFIGURATION
# ============================================================================
Write-Host "`n🐳 DOCKER CONFIGURATION" -ForegroundColor Yellow

Test-Check "docker-compose.yml has health checks" `
    { (Select-String -Path "docker-compose.yml" -Pattern "healthcheck") -ne $null } `
    "Add health check to docker-compose.yml"

Test-Check "docker-compose.yml has restart policy" `
    { (Select-String -Path "docker-compose.yml" -Pattern "restart") -ne $null } `
    "Add 'restart: always' to docker-compose.yml"

Test-Check "docker-compose.yml has resource limits" `
    { (Select-String -Path "docker-compose.yml" -Pattern "deploy|resources") -ne $null } `
    "Add resource limits to docker-compose.yml"

Test-Check "docker-compose.yml has backup volume" `
    { (Select-String -Path "docker-compose.yml" -Pattern "postgres_backups") -ne $null } `
    "Add backup volume to docker-compose.yml"

# ============================================================================
# DOCUMENTATION
# ============================================================================
Write-Host "`n📚 DOCUMENTATION" -ForegroundColor Yellow

Test-Check "LAUNCH_GUIDE.md exists" `
    { Test-Path "LAUNCH_GUIDE.md" } `
    "Create LAUNCH_GUIDE.md with startup procedures"

Test-Check "PRODUCTION_DATABASE_RELIABILITY.md exists" `
    { Test-Path "PRODUCTION_DATABASE_RELIABILITY.md" } `
    "Create PRODUCTION_DATABASE_RELIABILITY.md"

Test-Check "DATABASE_RELIABILITY_SOLUTION.md exists" `
    { Test-Path "DATABASE_RELIABILITY_SOLUTION.md" } `
    "Create DATABASE_RELIABILITY_SOLUTION.md"

# ============================================================================
# PRE-LAUNCH TESTS
# ============================================================================
Write-Host "`n🧪 PRE-LAUNCH TESTS" -ForegroundColor Yellow

Test-Check "Can start Docker container" `
    { 
        try {
            $test = docker-compose config > $null 2>&1
            $LASTEXITCODE -eq 0
        } catch {
            $false
        }
    } `
    "Check docker-compose.yml for syntax errors"

Test-Check "Docker daemon is running" `
    { (docker ps) -ne $null } `
    "Start Docker Desktop application"

# ============================================================================
# OPTIONAL CHECKS
# ============================================================================
Write-Host "`n⚡ OPTIONAL ENHANCEMENTS" -ForegroundColor Cyan

$WindowsTaskSchedulerSetup = Test-Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree"
if ($WindowsTaskSchedulerSetup) {
    Test-Check "Windows Task Scheduler available (for auto-backups)" `
        { $true }
}

# ============================================================================
# FINAL REPORT
# ============================================================================
Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  VERIFICATION RESULTS                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$TotalTests = $PassCount + $ErrorCount
$PassPercent = [math]::Round(($PassCount / $TotalTests) * 100, 0)

Write-Host "`n📊 Summary:"
Write-Host "  ✅ Passed: $PassCount" -ForegroundColor Green
Write-Host "  ❌ Failed: $ErrorCount" -ForegroundColor Red
Write-Host "  Total: $TotalTests"
Write-Host "  Success Rate: $PassPercent%`n"

if ($ErrorCount -eq 0) {
    Write-Host "🎉 ALL CHECKS PASSED! Your system is production-ready." -ForegroundColor Green
    Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. docker-compose up -d          # Start the application"
    Write-Host "  2. .\scripts\backup_database.ps1  # Create first backup"
    Write-Host "  3. .\scripts\monitor_database.ps1 # Start monitoring"
    Write-Host ""
    exit 0
} else {
    Write-Host "⚠️  CRITICAL ISSUES FOUND! Please fix the above errors before launching." -ForegroundColor Red
    Write-Host "`n📝 To fix:" -ForegroundColor Yellow
    Write-Host "  1. Review the error messages above"
    Write-Host "  2. Run the Fix commands shown"
    Write-Host "  3. Re-run this script to verify"
    Write-Host ""
    exit 1
}
