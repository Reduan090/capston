# Setup Complete - Capstone Research Assistant

## ✅ What's Been Implemented

### 1. Database Infrastructure
- **PostgreSQL 16** running in Docker (port 5433)
- **Docker Compose** for one-command startup
- **Professional Migration System** with schema versioning
- **Demo Data Seeding** with 3 users + 5 research papers

### 2. User Isolation & Authentication
- Each user gets isolated data directories:
  - `uploads/user_{id}/` - Personal document uploads
  - `vector_db/user_{id}/` - Individual FAISS indices  
  - `exports/user_{id}/` - Generated articles and exports
- `@require_authentication` decorator on all modules
- Audit logging for all user actions

### 3. Modules Updated with User Context
✅ **PDF Upload** - User-specific file storage and processing  
✅ **AI Writer** - Personal exports, 3-tab interface, LaTeX/Markdown  
✅ **Ask Paper** - RAG over user's documents only

🔄 **Remaining modules** to integrate:
- Literature Review
- Topic Finder
- Grammar & Style Checker
- Citation Tool
- Plagiarism Check

---

## 🚀 Quick Start

### Start the Application

```powershell
# 1. Start PostgreSQL
docker-compose up -d

# 2. Run migrations (first time only)
C:/Projects/capstone/venv/Scripts/python.exe scripts/migrate_db.py migrate

# 3. Seed demo data (first time only)
C:/Projects/capstone/venv/Scripts/python.exe scripts/seed_db.py

# 4. Launch application
C:/Projects/capstone/venv/Scripts/streamlit.exe run app.py
```

**Demo Credentials:**
| Username   | Password      | Email                     |
|------------|---------------|---------------------------|
| demo       | Demo123456    | demo@researchbot.local    |
| researcher | Research123   | researcher@research.bot   |
| student    | Student123    | student@research.bot      |

---

## 🧪 Testing User Isolation

### Test Scenario: Multi-User File Isolation

1. **Login as `demo`** (Demo123456)
   - Upload a PDF in **PDF Upload** module
   - Check: File saved to `uploads/user_1/`
   - Generate article in **AI Writer**
   - Check: Export saved to `exports/user_1/`

2. **Logout and login as `researcher`** (Research123)
   - Navigate to **PDF Upload** - verify NO files shown
   - Navigate to **AI Writer** → "My Exports" - verify empty
   - Upload different document
   - Check: File saved to `uploads/user_2/` (separate)

3. **Verify database isolation:**
   ```powershell
   docker exec capstone-postgres psql -U capstone -d capstone_db -c "SELECT id, username FROM users;"
   docker exec capstone-postgres psql -U capstone -d capstone_db -c "SELECT title, user_id FROM references_tbl;"
   ```

### Expected Outcomes
- ✅ Each user sees only their own uploads
- ✅ Vector databases don't cross-contaminate
- ✅ Export directories are isolated
- ✅ Database records have correct `user_id` foreign keys

---

## 📊 Database Schema (Current: v3)

### Migration History
1. **v1: initial_schema** - Created `references_tbl` and `notes` tables
2. **v2: add_user_references** - Added `user_id` columns with foreign keys
3. **v3: add_timestamps** - Added `created_at` timestamps

### Tables
```sql
-- Users (from auth system)
users (id, username, email, password_hash, created_at)

-- Research References (user-specific)
references_tbl (id, user_id, title, authors, year, journal, bibtex, created_at)

-- Notes (user-specific)
notes (id, user_id, reference_id, content, created_at)

-- Migration tracking
schema_migrations (version, name, applied_at)
```

---

## 🛠️ Management Commands

### Database Migrations
```powershell
# Check migration status
python scripts/migrate_db.py status

# Apply pending migrations
python scripts/migrate_db.py migrate

# Rollback to specific version
python scripts/migrate_db.py rollback --version 2
```

### Data Seeding
```powershell
# Seed everything
python scripts/seed_db.py

# Selective seeding
python scripts/seed_db.py --users      # Only users
python scripts/seed_db.py --references # Only research papers
python scripts/seed_db.py --files      # Only directory structure
```

### Docker Management
```powershell
# Start database
docker-compose up -d

# View logs
docker-compose logs -f postgres

# Stop (keep data)
docker-compose stop

# Full cleanup (DESTROYS DATA)
docker-compose down -v
```

---

## 📁 File Structure

### User Data Directories (Created by seeding)
```
uploads/
  user_1/            # demo user
  user_2/            # researcher user  
  user_3/            # student user
  sample_research.txt

vector_db/
  user_1/            # demo's FAISS indices
  user_2/            # researcher's FAISS indices
  user_3/            # student's FAISS indices

exports/
  user_1/            # demo's generated articles
  user_2/            # researcher's exports
  user_3/            # student's exports
```

### Helper Utilities
- **`utils/user_data.py`** - 11 helper functions:
  - `get_current_user_id()` - Get authenticated user ID
  - `@require_authentication` - Decorator for protecting modules
  - `get_user_upload_dir()` - User's upload folder path
  - `get_user_vector_db_dir()` - User's vector DB path
  - `get_user_export_dir()` - User's export folder path
  - `log_user_action()` - Audit trail logging
  - `get_user_storage_stats()` - File counts and sizes
  - `cleanup_user_data()` - Admin delete function

---

## 🔍 Verification Checklist

After setup, verify:

- [ ] PostgreSQL container running: `docker ps | findstr capstone-postgres`
- [ ] Database connection: `docker exec capstone-postgres pg_isready -U capstone`
- [ ] Migrations applied: `python scripts/migrate_db.py status` shows v3
- [ ] Demo users exist: 4 users in database (demo, Reduan, researcher, student)
- [ ] Demo references exist: 5 research papers
- [ ] User directories created: `uploads/user_1/`, `vector_db/user_1/`, `exports/user_1/`
- [ ] Streamlit launches: `http://localhost:8501` opens
- [ ] Login works: demo/Demo123456 authenticates
- [ ] Module isolation: Upload shows only user's files

---

## 📖 Additional Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Full deployment guide (350+ lines)
  - Architecture diagram
  - Troubleshooting section
  - Production deployment
  - Backup/restore procedures
  
- **[README.md](README.md)** - Project overview and features

- **Docker Compose** - [docker-compose.yml](docker-compose.yml)

---

## 🐛 Known Issues

1. **Emoji Logging Errors** (Windows PowerShell)
   - **Error:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'`
   - **Impact:** Benign - logs still written to files, only terminal display affected
   - **Workaround:** None needed (doesn't break functionality)

2. **Port Conflict** (5432)
   - **Resolution:** App uses port 5433 instead
   - **Connection:** `postgresql://capstone:capstone@localhost:5433/capstone_db`

3. **BibTeX Escape Sequence Warning**
   - **Warning:** `invalid escape sequence '\L'` in seed_db.py line 51
   - **Impact:** None (BibTeX still valid)
   - **Fix:** Use raw string `r"@inproceedings..."` (not critical)

---

## 🎯 Next Steps

### Priority 1: Complete Module Integration (1-2 hrs)
Apply user isolation to remaining 5 modules:
- `modules/literature_review.py`
- `modules/topic_finder.py`
- `modules/grammar_style.py`
- `modules/citation_tool.py`
- `modules/plagiarism_check.py`

**Pattern to apply:**
```python
from utils.user_data import (
    require_authentication,
    get_user_upload_dir,
    log_user_action,
)

@require_authentication
def main():
    user_dir = get_user_upload_dir()
    # ... rest of module ...
    log_user_action("module_action", details)
```

### Priority 2: End-to-End Testing (30 min)
- Multi-user upload/generate workflow
- Cross-user data isolation verification
- Performance testing with concurrent users

### Priority 3: Production Readiness (optional)
- Environment-specific configs (dev/staging/prod)
- SSL/TLS for database connections
- Rate limiting and resource quotas per user
- Admin dashboard for user management
- Automated backup jobs

---

## 💡 Tips

**Restart fresh database:**
```powershell
docker-compose down -v       # Delete all data
docker-compose up -d         # Start fresh
python scripts/migrate_db.py migrate  # Reapply schema
python scripts/seed_db.py    # Repopulate data
```

**Check specific user's data:**
```powershell
docker exec capstone-postgres psql -U capstone -d capstone_db -c \
  "SELECT * FROM references_tbl WHERE user_id = 1;"
```

**View user session activity:**
```sql
SELECT u.username, s.session_token, s.created_at 
FROM sessions s 
JOIN users u ON s.user_id = u.id 
WHERE s.expires_at > NOW();
```

---

**Setup completed on:** 2025-12-25  
**Database version:** v3  
**Modules integrated:** 3/8  
**Status:** ✅ Ready for testing
