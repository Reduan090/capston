"""
Database Migration System
Handles schema versioning and data migrations for PostgreSQL/SQLite.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import List, Callable
from config import logger, USE_POSTGRES, DATABASE_URL, DB_PATH

try:
    import psycopg
except ImportError:
    psycopg = None

import sqlite3


class Migration:
    """Represents a single database migration."""
    
    def __init__(self, version: int, name: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.applied_at = None


class MigrationManager:
    """Manages database migrations with version control."""
    
    def __init__(self):
        self.migrations: List[Migration] = []
        self._init_migration_table()
    
    def _get_connection(self):
        """Get database connection."""
        if USE_POSTGRES and psycopg is not None:
            return psycopg.connect(DATABASE_URL)
        else:
            return sqlite3.connect(DB_PATH)
    
    def _init_migration_table(self):
        """Create migrations table if it doesn't exist."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if USE_POSTGRES and psycopg is not None:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            conn.commit()
            conn.close()
            logger.info("Migration table initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize migration table: {e}")
            raise
    
    def register_migration(self, migration: Migration):
        """Register a migration."""
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def get_current_version(self) -> int:
        """Get the current schema version."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT MAX(version) FROM schema_migrations")
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] is not None else 0
            
        except Exception as e:
            logger.warning(f"Could not get current version: {e}")
            return 0
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied yet."""
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]
    
    def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            logger.info(f"Applying migration {migration.version}: {migration.name}")
            
            # Execute migration SQL
            for statement in migration.up_sql.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            # Record migration
            if USE_POSTGRES and psycopg is not None:
                cursor.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
                    (migration.version, migration.name)
                )
            else:
                cursor.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                    (migration.version, migration.name)
                )
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Migration {migration.version} applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration {migration.version} failed: {e}")
            conn.rollback()
            conn.close()
            return False
    
    def migrate_to_latest(self) -> bool:
        """Apply all pending migrations."""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return True
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        for migration in pending:
            if not self.apply_migration(migration):
                logger.error(f"Migration stopped at version {migration.version}")
                return False
        
        logger.info(f"✅ All migrations applied. Current version: {self.get_current_version()}")
        return True
    
    def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration (if down_sql provided)."""
        if not migration.down_sql:
            logger.error(f"No rollback defined for migration {migration.version}")
            return False
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            logger.info(f"Rolling back migration {migration.version}: {migration.name}")
            
            # Execute rollback SQL
            for statement in migration.down_sql.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            # Remove migration record
            cursor.execute(
                "DELETE FROM schema_migrations WHERE version = ?",
                (migration.version,)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Migration {migration.version} rolled back")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            conn.rollback()
            conn.close()
            return False
    
    def show_status(self):
        """Display migration status."""
        current = self.get_current_version()
        pending = self.get_pending_migrations()
        
        print("\n" + "="*60)
        print("DATABASE MIGRATION STATUS")
        print("="*60)
        print(f"Current Version: {current}")
        print(f"Database: {'PostgreSQL' if (USE_POSTGRES and psycopg) else 'SQLite'}")
        print(f"Pending Migrations: {len(pending)}")
        print("="*60)
        
        if pending:
            print("\nPending:")
            for m in pending:
                print(f"  • v{m.version}: {m.name}")
        
        print("\nApplied:")
        for m in self.migrations:
            if m.version <= current:
                print(f"  ✓ v{m.version}: {m.name}")
        print("="*60 + "\n")


# Define migrations
def get_migrations() -> List[Migration]:
    """Get all registered migrations."""
    
    migrations = []
    
    # Migration 001: Initial Schema
    migrations.append(Migration(
        version=1,
        name="initial_schema",
        up_sql="""
        CREATE TABLE IF NOT EXISTS references_tbl (
            id SERIAL PRIMARY KEY,
            title TEXT,
            authors TEXT,
            year TEXT,
            doi TEXT,
            bibtex TEXT
        );
        
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            content TEXT,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        """.replace("SERIAL", "INTEGER PRIMARY KEY AUTOINCREMENT" if not USE_POSTGRES else "SERIAL")
           .replace("TIMESTAMPTZ", "DATETIME" if not USE_POSTGRES else "TIMESTAMPTZ"),
        down_sql="""
        DROP TABLE IF EXISTS notes;
        DROP TABLE IF EXISTS references_tbl;
        """
    ))
    
    # Migration 002: User-specific data
    migrations.append(Migration(
        version=2,
        name="add_user_references",
        up_sql="""
        ALTER TABLE references_tbl ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);
        ALTER TABLE notes ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);
        """.replace("IF NOT EXISTS", "" if not USE_POSTGRES else "IF NOT EXISTS"),
        down_sql="""
        ALTER TABLE references_tbl DROP COLUMN IF EXISTS user_id;
        ALTER TABLE notes DROP COLUMN IF EXISTS user_id;
        """
    ))
    
    # Migration 003: Add created_at timestamps
    migrations.append(Migration(
        version=3,
        name="add_timestamps",
        up_sql="""
        ALTER TABLE references_tbl ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP;
        """.replace("IF NOT EXISTS", "" if not USE_POSTGRES else "IF NOT EXISTS")
           .replace("TIMESTAMPTZ", "DATETIME" if not USE_POSTGRES else "TIMESTAMPTZ"),
        down_sql="""
        ALTER TABLE references_tbl DROP COLUMN IF EXISTS created_at;
        """
    ))
    
    return migrations


def main():
    """Run migrations from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("command", choices=["migrate", "status", "rollback"], 
                       help="Migration command to execute")
    parser.add_argument("--version", type=int, help="Specific version to rollback to")
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    # Register all migrations
    for migration in get_migrations():
        manager.register_migration(migration)
    
    if args.command == "status":
        manager.show_status()
    
    elif args.command == "migrate":
        print("\n🔄 Running database migrations...\n")
        success = manager.migrate_to_latest()
        if success:
            print("\n✅ All migrations completed successfully!\n")
        else:
            print("\n❌ Migration failed. Check logs for details.\n")
            sys.exit(1)
    
    elif args.command == "rollback":
        if not args.version:
            print("❌ Please specify --version for rollback")
            sys.exit(1)
        
        migration = next((m for m in manager.migrations if m.version == args.version), None)
        if migration:
            success = manager.rollback_migration(migration)
            if success:
                print(f"\n✅ Rolled back to version {args.version}\n")
            else:
                print(f"\n❌ Rollback failed\n")
                sys.exit(1)
        else:
            print(f"❌ Migration version {args.version} not found")
            sys.exit(1)


if __name__ == "__main__":
    main()
