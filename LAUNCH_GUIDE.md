# 🚀 PRODUCTION DEPLOYMENT: QUICK START GUIDE

## ONE-TIME SETUP (Before First Launch)

### 1. Verify Prerequisites
```powershell
# Check Docker is installed
docker --version

# Check Docker Compose
docker-compose --version

# Ensure at least 4GB RAM allocated to Docker
```

### 2. Create Backup Directory
```powershell
mkdir postgres-backups
```

### 3. First Run
```powershell
# Start the app (creates database, runs migrations)
docker-compose up -d

# Wait for database to be ready (check health)
docker ps  # Look for "healthy" status on postgres

# Initialize database schema
docker exec capstone-postgres psql -U capstone -d capstone_db -f /var/scripts/init_db.sql
```

---

## DAILY OPERATIONS

### Start Application
```powershell
docker-compose up -d
```

### Stop Application
```powershell
docker-compose down
```

### Check Status
```powershell
# Quick status
docker ps

# See if database is healthy
docker ps | Select-String postgres

# View database logs
docker logs capstone-postgres
```

### Backup Database (Run Daily)
```powershell
# Create backup
powershell -ExecutionPolicy Bypass -File scripts\backup_database.ps1

# Should create file like: postgres-backups\capstone_db_backup_2025-12-27_140530.dump
```

### Monitor in Real-Time
```powershell
# Interactive dashboard (auto-refreshes every 5 seconds)
powershell -ExecutionPolicy Bypass -File scripts\monitor_database.ps1

# Commands in monitor:
# B - Backup now
# L - View logs  
# R - Restart
# S - Stop
```

---

## TROUBLESHOOTING

### Problem: "Database Connection Failed"
```powershell
# 1. Check if container is running
docker ps

# 2. If not running, start it
docker-compose up -d

# 3. If running but not responding
docker restart capstone-postgres

# 4. Wait and check again
Start-Sleep -Seconds 20
docker ps
```

### Problem: "Out of Disk Space"
```powershell
# See what's taking space
Get-ChildItem postgres-backups | Measure-Object -Property Length -Sum

# Delete old backups (keep 3 recent)
Get-ChildItem postgres-backups\*.dump | 
  Sort-Object CreationTime -Descending | 
  Select-Object -Skip 3 | 
  Remove-Item
```

### Problem: "Need to Restore from Backup"
```powershell
# 1. Stop everything
docker-compose down

# 2. Remove corrupted data
Remove-Item postgres-data -Recurse -Force

# 3. Start fresh
docker-compose up -d

# 4. Restore backup (will be created automatically from your backup file)
# The system will pull from postgres-backups/
```

---

## MONITORING CHECKLIST

Daily (takes 30 seconds):
- [ ] Run: `docker ps` → PostgreSQL shows "healthy"
- [ ] Run: `docker logs capstone-postgres --tail 20` → No error messages
- [ ] Run: `backup_database.ps1` → Backup completes successfully

Weekly:
- [ ] Run: `monitor_database.ps1` → Review disk usage
- [ ] Check: `postgres-backups/` → At least 3 backups present
- [ ] Review: `logs/database_monitor.log` → No unexpected restarts

---

## EMERGENCY PROCEDURES

### If Database Won't Start (30 seconds)
```powershell
docker restart capstone-postgres
Start-Sleep -Seconds 25
docker ps  # Check if healthy now
```

### If Container Keeps Crashing (5 minutes)
```powershell
# Check logs for root cause
docker logs capstone-postgres | tail -50

# Common issues:
# - Not enough disk space: `Remove-Item postgres-backups -Recurse` (keep newest)
# - Corrupted data: See "Restore from Backup" above
# - Port conflict: `docker ps` shows multiple postgres containers?
```

### If Complete Data Loss (15 minutes)
```powershell
# 1. Stop app
docker-compose down

# 2. Restore from latest backup
$BackupFile = Get-ChildItem postgres-backups\*.dump | Sort CreationTime -Desc | Select -First 1
docker cp $BackupFile.FullName capstone-postgres:/var/backups/backup.dump
docker start capstone-postgres
docker exec capstone-postgres pg_restore -U capstone -d capstone_db /var/backups/backup.dump

# 3. Restart app
docker-compose up -d
```

---

## PERFORMANCE TUNING

### For Slow Queries
```powershell
# Check what's in database
docker exec capstone-postgres psql -U capstone -d capstone_db -c "SELECT count(*) FROM references_tbl;"

# If > 100k rows, optimize indexes
docker exec capstone-postgres psql -U capstone -d capstone_db -c "ANALYZE;"
```

### For High Memory Usage
Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_INITDB_ARGS: "-c shared_buffers=256MB"

deploy:
  resources:
    limits:
      memory: 2G
```

Then restart: `docker-compose down && docker-compose up -d`

---

## CONTACTS & ESCALATION

| Issue | Action | Time |
|-------|--------|------|
| Container not running | `docker restart capstone-postgres` | 30s |
| Database errors in logs | Check `docker logs capstone-postgres` | 5m |
| Disk full | Delete old backups | 5m |
| Data corruption | Restore from `postgres-backups/` | 15m |
| Still broken | Escalate to DevOps | +time |

---

## KEY FILES & LOCATIONS

```
📁 Production Setup:
├── docker-compose.yml          # Main configuration
├── postgres-data/              # Database files (persistent)
├── postgres-backups/           # Daily backups
├── scripts/
│   ├── backup_database.ps1     # Run daily backups
│   ├── monitor_database.ps1    # Real-time dashboard
│   └── init_db.sql             # Schema initialization
└── logs/
    └── database_monitor.log    # Monitoring logs

💾 Critical Backups:
postgres-backups/capstone_db_backup_YYYY-MM-DD_HHMMSS.dump
  (Keep at least 3 recent backups at all times!)
```

---

## ✅ LAUNCH CHECKLIST

Before going live:
- [ ] Test complete startup: `docker-compose up -d` then `docker ps`
- [ ] Test backup: `backup_database.ps1`
- [ ] Test restore: Remove postgres-data, restart, verify data restored
- [ ] Test monitoring: `monitor_database.ps1`
- [ ] Test failover: Kill container, verify auto-restart
- [ ] Document team access and procedures
- [ ] Schedule daily backups (Windows Task Scheduler)
- [ ] Set up monitoring alerts

---

**You're ready for production! 🎉**
