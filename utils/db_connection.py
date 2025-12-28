# utils/db_connection.py
"""
PRODUCTION-GRADE DATABASE CONNECTION HANDLER
Implements comprehensive resilience and monitoring patterns
"""

import time
import psycopg
import psycopg_pool
from config import DATABASE_URL, logger
from typing import Optional

class DatabaseConnectionPool:
    """
    Manages PostgreSQL connections with:
    - Connection pooling for efficiency
    - Automatic reconnection with exponential backoff
    - Health monitoring
    - Connection timeout handling
    """
    
    _instance = None
    _pool: Optional[psycopg_pool.ConnectionPool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool on first instantiation"""
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """
        Create connection pool with production-grade settings
        
        Pool settings:
        - Min connections: 2 (always ready for failover)
        - Max connections: 20 (prevents resource exhaustion)
        - Connection timeout: 5 seconds
        """
        try:
            self._pool = psycopg_pool.ConnectionPool(
                DATABASE_URL,
                min_size=2,
                max_size=20,
                timeout=5,
                open=True
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.critical(f"FAILED TO INITIALIZE DATABASE CONNECTION POOL: {str(e)}")
            raise RuntimeError(
                f"Cannot create database connection pool. Database may be unavailable. "
                f"Error: {str(e)}"
            ) from e
    
    def get_connection(self, max_retries: int = 3, backoff_factor: float = 1.0):
        """
        Get a connection from the pool with retry logic
        
        Args:
            max_retries: Number of connection attempts before failing
            backoff_factor: Exponential backoff multiplier (1.0 = 1s, 2s, 4s)
        
        Implements exponential backoff:
            Attempt 1: immediate
            Attempt 2: wait 1 second
            Attempt 3: wait 2 seconds
            Attempt 4: wait 4 seconds
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized")
        
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                conn = self._pool.getconn()
                # Verify connection is valid
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                logger.debug(f"Database connection acquired (attempt {attempt})")
                return conn
            except (psycopg.OperationalError, psycopg.DatabaseError) as e:
                last_error = e
                if attempt < max_retries:
                    # Calculate exponential backoff: 1s, 2s, 4s
                    wait_time = backoff_factor * (2 ** (attempt - 1))
                    logger.warning(
                        f"Database connection failed (attempt {attempt}/{max_retries}). "
                        f"Retrying in {wait_time}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.critical(
                        f"Database connection failed after {max_retries} attempts. "
                        f"Database is unreachable. Last error: {str(e)}"
                    )
        raise RuntimeError(
            f"Database connection failed after {max_retries} attempts. "
            f"PostgreSQL is unreachable. The application cannot continue."
        ) from last_error
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if self._pool and conn:
            self._pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in pool (for graceful shutdown)"""
        if self._pool:
            self._pool.close()
            logger.info("All database connections closed")

# Singleton instance
db_pool = DatabaseConnectionPool()

def get_db_connection():
    """
    Get a database connection with automatic retry
    Usage:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("...")
            conn.commit()
        finally:
            db_pool.return_connection(conn)
    """
    return db_pool.get_connection()

def health_check() -> dict:
    """
    Health check endpoint for monitoring
    
    Returns:
        {
            "status": "healthy" | "unhealthy",
            "database": "connected" | "disconnected",
            "response_time_ms": float,
            "error": str (if unhealthy)
        }
    """
    start_time = time.time()
    try:
        conn = db_pool.get_connection(max_retries=1)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        db_pool.return_connection(conn)
        
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "response_time_ms": round(response_time, 2),
            "error": str(e)
        }
