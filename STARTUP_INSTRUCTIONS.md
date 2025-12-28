# 🚀 STARTUP INSTRUCTIONS

## ⚠️ Docker Not Running

Docker is installed but **not currently running**. You need to start it:

### Option 1: Quick Start (Recommended)
```powershell
# 1. Open Docker Desktop from Start Menu
#    Search for "Docker Desktop" and click it
#    Wait 2-3 minutes for it to fully initialize

# 2. Once running, verify Docker is ready
docker ps

# 3. Then start the application
docker-compose up -d
```

### Option 2: Start Docker Service (If Available)
```powershell
# Try starting the Docker service directly
Start-Service com.docker.service

# Wait 30 seconds
Start-Sleep -Seconds 30

# Verify it's running
docker ps

# If successful, start the app
docker-compose up -d
```

### Option 3: Manual Startup via PowerShell
```powershell
# If Docker Desktop is installed, try:
& "C:\Program Files\Docker\Docker\Docker.exe"

# Then wait 3 minutes and run:
docker-compose up -d
```

---

## ✅ After Docker is Running

Once Docker Desktop is running (verify with `docker ps`):

### Start the Application
```powershell
# Start all services (PostgreSQL + App)
docker-compose up -d

# This will:
# ✅ Create PostgreSQL container
# ✅ Initialize database schema
# ✅ Start your application
# Takes 20-30 seconds
```

### Verify It's Running
```powershell
# Check container status
docker ps

# You should see "capstone-postgres" with "healthy" status

# View app logs
docker logs capstone-postgres

# If you see errors, check the logs
docker logs capstone-postgres --tail 50
```

### Create First Backup
```powershell
# Backup the database
.\scripts\backup_database.ps1

# Creates: postgres-backups\capstone_db_backup_YYYY-MM-DD_HHMMSS.dump
```

### Monitor System
```powershell
# Launch interactive monitoring dashboard
.\scripts\monitor_database.ps1

# Shows:
# - Database health
# - Container status
# - Disk usage
# - Real-time metrics
```

---

## 🆘 Troubleshooting

### "Docker daemon is not running"
**Fix**: 
1. Open Docker Desktop application
2. Wait 2-3 minutes for initialization
3. Run `docker ps` to verify
4. Then `docker-compose up -d`

### "Cannot connect to Docker daemon"
**Fix**:
1. Check if Docker Desktop is running (look for Docker icon in taskbar)
2. If not running, open it manually
3. Wait for initialization
4. Try again

### "docker-compose: command not found"
**Fix**: 
1. Docker Compose is bundled with Docker Desktop
2. Make sure Docker Desktop is fully installed
3. Restart terminal/PowerShell
4. Try again

---

## ⏱️ Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Open Docker Desktop | Now | ⏳ Waiting |
| Docker initializes | 2-3 min | ⏳ Initializing |
| `docker ps` works | +1 min | ✅ Ready |
| `docker-compose up -d` | +30 sec | ✅ Starting |
| Database healthy | +20 sec | ✅ Running |
| First backup | +30 sec | ✅ Complete |
| **TOTAL TIME** | **~5 minutes** | 🎉 **DONE** |

---

## 📞 Still Having Issues?

1. **Check Docker installation**: `docker --version`
2. **Check Docker daemon**: `docker ps`
3. **Check Docker Compose**: `docker-compose --version`
4. **See detailed logs**: `docker logs capstone-postgres --tail 100`
5. **Read the guide**: See `LAUNCH_GUIDE.md`

---

## 🎯 Next Steps

Once Docker is running and app is started:

```powershell
# 1. Verify database is healthy
docker ps  # Look for "healthy" status

# 2. Create first backup
.\scripts\backup_database.ps1

# 3. Monitor system (optional)
.\scripts\monitor_database.ps1

# 4. Access your application
# Open browser to: http://localhost:8501
# (or wherever your app is configured)
```

---

**⏸️ WAITING FOR YOU TO OPEN DOCKER DESKTOP...**

Once open and initialized, run:
```powershell
docker-compose up -d
```
