# Deployment & Setup Guide

## Quick Start (Production Ready)

### Prerequisites
- Docker & Docker Compose installed
- Python 3.10+ with venv
- Git

### One-Command Setup

```bash
# 1. Start PostgreSQL (first time only)
docker-compose up -d

# 2. Activate Python environment
# On Windows
venv\Scripts\Activate.ps1

# On macOS/Linux
source venv/bin/activate

# 3. Install dependencies (first time only)
pip install -r requirements.txt

# 4. Initialize authentication database
python scripts/setup_auth.py

# 5. Run the app
streamlit run app.py
```

The app will be available at: **http://localhost:8501**

---

## Architecture

```
┌─────────────────────────────────────────┐
│     Streamlit Web UI (Port 8501)        │
│  - Authentication & Session Management  │
│  - Document Upload & Processing         │
│  - AI-Powered Features                  │
└──────────────┬──────────────────────────┘
               │
               ├─ User Data (SQLite/Postgres)
               ├─ Vector DB (FAISS)
               ├─ LLM (Ollama)
               └─ External APIs (Semantic Scholar, CrossRef)
               │
               ▼
┌──────────────────────────────────────────┐
│    PostgreSQL Database (Port 5433)      │
│  - User accounts & authentication       │
│  - Research metadata & citations        │
│  - Login history & audit trail          │
└──────────────────────────────────────────┘
```

---

## Database Configuration

### Connection Details
- **Host:** localhost
- **Port:** 5433
- **User:** capstone
- **Password:** capstone
- **Database:** capstone_db

### Environment Variables
Set in `.env` file (auto-loaded by config.py):

```env
USE_POSTGRES=true
DATABASE_URL=postgresql://capstone:capstone@localhost:5433/capstone_db
```

---

## Container Management

### Start Services
```bash
# Start PostgreSQL in background
docker-compose up -d

# View running containers
docker ps
```

### View Logs
```bash
# PostgreSQL logs
docker-compose logs -f postgres

# Follow all logs
docker-compose logs -f
```

### Stop Services
```bash
# Stop all containers (keep data)
docker-compose stop

# Remove containers but keep volumes
docker-compose down

# Remove everything including data (clean slate)
docker-compose down -v
```

### Verify Database Connection
```bash
# Test from terminal
python -c "import psycopg; conn=psycopg.connect('postgresql://capstone:capstone@localhost:5433/capstone_db'); print('Connected!')"

# Or with psql inside container
docker exec capstone-postgres psql -U capstone -d capstone_db -c "\conninfo"
```

---

## Troubleshooting

### PostgreSQL Won't Start
```bash
# Check if port 5433 is already in use
netstat -ano | findstr :5433

# View container logs
docker logs capstone-postgres

# Rebuild from scratch
docker-compose down -v
docker-compose up -d
```

### Connection Refused
```bash
# Wait for Postgres to be ready (healthcheck)
docker-compose up -d
sleep 10

# Verify connection
docker exec capstone-postgres psql -U capstone -d capstone_db -c "SELECT 1"
```

### Password Authentication Failed
```bash
# Reset password inside container
docker exec capstone-postgres psql -U capstone -d capstone_db -c "ALTER USER capstone WITH PASSWORD 'capstone';"
```

### App Can't Find Database
- Verify `.env` file exists with `USE_POSTGRES=true`
- Ensure Docker container is running: `docker ps | grep capstone-postgres`
- Check connection URL matches Docker port (5433, not 5432)

---

## Development Workflow

### Local Testing
```bash
# Terminal 1: Start database
docker-compose up -d

# Terminal 2: Run app
streamlit run app.py

# Terminal 3: Run tests
pytest tests/

# Terminal 4: Check logs
docker-compose logs -f postgres
```

### Making Changes
1. Edit Python files normally
2. Streamlit auto-reloads on save
3. Database changes: restart container with `docker-compose restart postgres`
4. Dependency changes: update `requirements.txt` and `pip install -r requirements.txt`

---

## Production Deployment

### Cloud Deployment (Example: Railway/Render)

1. **Push to Git**
   ```bash
   git add .
   git commit -m "Production ready"
   git push
   ```

2. **Set Environment Variables**
   ```
   USE_POSTGRES=true
   DATABASE_URL=postgresql://user:pass@cloud-db-host:5432/capstone_db
   ```

3. **Deploy Steps**
   - Connect GitHub repo to cloud platform
   - Select Python environment
   - Set port to 8501
   - Deploy

### Docker Build for Production
```bash
# Build custom image
docker build -t capstone:latest .

# Run with production settings
docker run -p 8501:8501 \
  -e DATABASE_URL="postgresql://..." \
  -e USE_POSTGRES="true" \
  capstone:latest
```

---

## Backup & Restore

### Backup Database
```bash
# Export dump
docker exec capstone-postgres pg_dump -U capstone capstone_db > backup.sql

# Save volumes
docker run --rm -v capstone_postgres_data:/data -v $(pwd):/backup \
  busybox tar czf /backup/db_backup.tar.gz /data
```

### Restore Database
```bash
# Restore from dump
docker exec -i capstone-postgres psql -U capstone capstone_db < backup.sql
```

---

## Monitoring & Logs

### View All Logs
```bash
# Last 100 lines
docker-compose logs --tail=100

# Real-time tail
docker-compose logs -f

# PostgreSQL only
docker-compose logs postgres -f
```

### Database Statistics
```bash
# Connect to database
docker exec -it capstone-postgres psql -U capstone -d capstone_db

# Inside psql:
\dt                           # List tables
\di                           # List indexes
SELECT * FROM users;         # View users
SELECT * FROM login_history; # View login attempts
```

---

## Security Notes

### For Production
- Change default credentials in `.env`
- Use environment-specific secrets management
- Enable SSL/TLS for database connections
- Implement rate limiting on auth endpoints
- Regular security audits of dependencies
- Use strong passwords for all accounts
- Enable database backups to secure storage
- Monitor login attempts for anomalies

### Secrets Management
```bash
# Use .env.local (not tracked in git)
cp .env .env.local
# Edit .env.local with production secrets
```

---

## Quick Commands Cheat Sheet

```bash
# Start everything
docker-compose up -d

# Check status
docker ps

# View logs
docker-compose logs -f

# Stop all
docker-compose stop

# Clean up (keep data)
docker-compose down

# Full reset
docker-compose down -v

# Run app
streamlit run app.py

# Test auth
python scripts/test_auth.py

# Initialize demo account
python scripts/setup_auth.py
```

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify connection: `docker exec capstone-postgres psql -U capstone -d capstone_db -c "SELECT 1"`
3. Reset everything: `docker-compose down -v && docker-compose up -d`
4. Check Python venv: `pip list | grep psycopg`

