# utils/database.py
"""
DATABASE OPERATIONS MODULE
Uses connection pooling and retry logic for production reliability
"""

from typing import List, Tuple, Dict, Any
from config import logger
from utils.db_connection import get_db_connection, db_pool
import psycopg

def init_db() -> None:
    """
    Initialize the PostgreSQL database schema.
    Uses retry logic - if database is down, fails with clear error.
    """
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    """
                    CREATE TABLE IF NOT EXISTS references_tbl (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        authors TEXT,
                        year TEXT,
                        doi TEXT UNIQUE,
                        bibtex TEXT,
                        user_id INTEGER,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                c.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        user_id INTEGER,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                # Create indexes for faster queries
                c.execute(
                    "CREATE INDEX IF NOT EXISTS idx_references_user_id ON references_tbl(user_id)"
                )
                c.execute(
                    "CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id)"
                )
            conn.commit()
            logger.info("✅ PostgreSQL database initialized successfully")
        finally:
            db_pool.return_connection(conn)
    
    except Exception as e:
        logger.critical(f"❌ CRITICAL: Database initialization failed: {str(e)}")
        raise RuntimeError(
            "Database initialization failed. PostgreSQL is not available. "
            "Please ensure Docker containers are running: 'docker-compose up -d'"
        ) from e


def add_reference(
    title: str, authors: str, year: str, doi: str, bibtex: str, user_id: int = None
) -> Dict[str, Any]:
    """Add reference with automatic retry logic"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    """
                    INSERT INTO references_tbl (title, authors, year, doi, bibtex, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                    """,
                    (title, authors, year, doi, bibtex, user_id),
                )
                result = c.fetchone()
            conn.commit()
            logger.info(f"✅ Added reference: {title} (ID: {result[0]})")
            return {"success": True, "id": result[0], "created_at": result[1]}
        finally:
            db_pool.return_connection(conn)
    
    except psycopg.IntegrityError as e:
        logger.warning(f"⚠️ Duplicate reference (DOI already exists): {doi}")
        raise ValueError(f"Reference with DOI '{doi}' already exists") from e
    except Exception as e:
        logger.error(f"❌ Failed to add reference: {str(e)}")
        raise RuntimeError("Database operation failed. Please try again.") from e


def get_references(user_id: int = None) -> List[Dict[str, Any]]:
    """Get all references with automatic retry logic"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as c:
                if user_id is not None:
                    c.execute(
                        """
                        SELECT id, title, authors, year, doi, bibtex, created_at, updated_at
                        FROM references_tbl
                        WHERE user_id = %s OR user_id IS NULL
                        ORDER BY created_at DESC
                        """,
                        (user_id,),
                    )
                else:
                    c.execute(
                        """
                        SELECT id, title, authors, year, doi, bibtex, created_at, updated_at
                        FROM references_tbl
                        ORDER BY created_at DESC
                        """
                    )
                
                rows = c.fetchall()
                return [
                    {
                        "id": row[0],
                        "title": row[1],
                        "authors": row[2],
                        "year": row[3],
                        "doi": row[4],
                        "bibtex": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                    }
                    for row in rows
                ]
        finally:
            db_pool.return_connection(conn)
    
    except Exception as e:
        logger.error(f"❌ Failed to retrieve references: {str(e)}")
        raise RuntimeError("Database operation failed. Please try again.") from e


def delete_reference(reference_id: int, user_id: int = None) -> Dict[str, Any]:
    """Delete a reference with authorization check"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as c:
                # Verify user owns this reference
                if user_id is not None:
                    c.execute(
                        "DELETE FROM references_tbl WHERE id = %s AND (user_id = %s OR user_id IS NULL)",
                        (reference_id, user_id),
                    )
                else:
                    c.execute("DELETE FROM references_tbl WHERE id = %s", (reference_id,))
                
                deleted = c.rowcount
            conn.commit()
            
            if deleted > 0:
                logger.info(f"✅ Deleted reference ID: {reference_id}")
                return {"success": True, "deleted": deleted}
            else:
                logger.warning(f"⚠️ Reference not found or unauthorized: {reference_id}")
                return {"success": False, "deleted": 0, "message": "Reference not found"}
        finally:
            db_pool.return_connection(conn)
    
    except Exception as e:
        logger.error(f"❌ Failed to delete reference: {str(e)}")
        raise RuntimeError("Database operation failed.") from e
