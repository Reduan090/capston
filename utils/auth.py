"""
User Authentication Module - Industry-Grade Implementation
Uses bcrypt for password hashing and SQLite for user storage.
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import bcrypt
from config import logger, USE_POSTGRES, DATABASE_URL

try:
    import psycopg
except Exception:
    psycopg = None

# Database path for users
AUTH_DB_PATH = Path("db/auth.db")
AUTH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class AuthenticationManager:
    """Manages user authentication, registration, and session management."""

    def __init__(self, db_path: str = str(AUTH_DB_PATH)):
        self.db_path = db_path
        if not (USE_POSTGRES and psycopg is not None):
            # SQLite performance pragmas
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=10000')  # 10 seconds
            conn.execute('PRAGMA synchronous=FULL')  # Ensure all writes are synced
            conn.close()
        self._init_auth_db()
        self._ensure_demo_user()  # Create demo account on startup

    def _init_auth_db(self) -> None:
        """Initialize authentication database with users and sessions tables."""
        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute(
                            """
                            CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY,
                                username TEXT UNIQUE NOT NULL,
                                email TEXT UNIQUE NOT NULL,
                                password_hash TEXT NOT NULL,
                                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                                is_active BOOLEAN DEFAULT TRUE
                            )
                            """
                        )
                        c.execute(
                            """
                            CREATE TABLE IF NOT EXISTS sessions (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                                session_token TEXT UNIQUE NOT NULL,
                                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                                expires_at TIMESTAMPTZ NOT NULL
                            )
                            """
                        )
                        c.execute(
                            """
                            CREATE TABLE IF NOT EXISTS login_history (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                                login_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                                success BOOLEAN DEFAULT TRUE,
                                ip_address TEXT
                            )
                            """
                        )
                    conn.commit()
                logger.info("✅ Authentication database initialized")
                return

            # SQLite fallback
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=5000')
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS login_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT 1,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("✅ Authentication database initialized")
        except Exception as e:
            logger.error(f"❌ Auth DB initialization error: {e}")
            raise

    def register_user(
        self, username: str, email: str, password: str
    ) -> Tuple[bool, str]:
        """
        Register a new user with bcrypt-hashed password.
        
        Args:
            username: Unique username
            email: User email
            password: Plain text password (will be hashed)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self._validate_password(password):
            return False, "❌ Password must be at least 8 characters with uppercase, lowercase, and numbers"

        if len(username) < 3 or len(username) > 20:
            return False, "❌ Username must be 3-20 characters"

        if "@" not in email or "." not in email.split("@")[1]:
            return False, "❌ Invalid email format"

        try:
            # Hash password with bcrypt
            password_hash_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        # Store as TEXT for portability
                        c.execute(
                            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                            (username, email, password_hash_bytes.decode()),
                        )
                    conn.commit()
            else:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash_bytes),
                )
                conn.commit()
                # Verify the insert was successful
                c.execute("SELECT id FROM users WHERE username = ?", (username,))
                result = c.fetchone()
                if not result:
                    conn.close()
                    logger.error(f"❌ Registration verification failed for {username}")
                    return False, "❌ Registration failed - please try again"
                conn.close()

            logger.info(f"✅ User registered: {username}")
            return True, "✅ Registration successful! Please log in."

        except sqlite3.IntegrityError as e:
            logger.warning(f"⚠️ Registration failed for {username}: {str(e)}")
            if "username" in str(e):
                return False, "❌ Username already exists"
            elif "email" in str(e):
                return False, "❌ Email already registered"
            return False, "❌ Registration failed"
        except Exception as e:
            logger.error(f"❌ Unexpected registration error: {e}")
            return False, f"❌ Registration error: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user and create session.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str, session_token: str or None)
        """
        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute(
                            "SELECT id, password_hash FROM users WHERE username = %s AND is_active = TRUE",
                            (username,),
                        )
                        result = c.fetchone()
                        if result is None:
                            logger.warning(f"⚠️ Failed login attempt: user {username} not found")
                            return False, "❌ Invalid username or password", None
                        user_id, password_hash = result
                        if isinstance(password_hash, str):
                            password_hash_bytes = password_hash.encode()
                        else:
                            password_hash_bytes = password_hash
                        if not bcrypt.checkpw(password.encode(), password_hash_bytes):
                            logger.warning(f"⚠️ Failed login attempt: wrong password for {username}")
                            c.execute(
                                "INSERT INTO login_history (user_id, success) VALUES (%s, %s)",
                                (user_id, False),
                            )
                            conn.commit()
                            return False, "❌ Invalid username or password", None
                        session_token = self._create_session(user_id)
                        c.execute(
                            "INSERT INTO login_history (user_id, success) VALUES (%s, %s)",
                            (user_id, True),
                        )
                        conn.commit()
                        logger.info(f"✅ User authenticated: {username}")
                        return True, "✅ Login successful!", session_token
            
            # SQLite path
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=10000')
            c = conn.cursor()
            c.execute(
                "SELECT id, password_hash FROM users WHERE username = ? AND is_active = 1",
                (username,),
            )
            result = c.fetchone()

            if result is None:
                conn.close()
                logger.warning(f"⚠️ Failed login attempt: user {username} not found")
                return False, "❌ Invalid username or password", None

            user_id, password_hash = result

            # Verify password with bcrypt
            if not bcrypt.checkpw(password.encode(), password_hash):
                logger.warning(f"⚠️ Failed login attempt: wrong password for {username}")
                c.execute(
                    "INSERT INTO login_history (user_id, success) VALUES (?, ?)",
                    (user_id, 0),
                )
                conn.commit()
                conn.close()
                return False, "❌ Invalid username or password", None

            # Create session token
            session_token = self._create_session(user_id)

            # Log successful login
            c.execute(
                "INSERT INTO login_history (user_id, success) VALUES (?, ?)",
                (user_id, 1),
            )
            conn.commit()
            conn.close()

            logger.info(f"✅ User authenticated: {username}")
            return True, "✅ Login successful!", session_token

        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False, f"❌ Authentication error: {str(e)}", None

    def _create_session(self, user_id: int, days: int = 7) -> str:
        """Create a new session for user."""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=days)

        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute(
                            "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
                            (user_id, session_token, expires_at),
                        )
                    conn.commit()
                return session_token
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)",
                (user_id, session_token, expires_at),
            )
            conn.commit()
            conn.close()
            return session_token
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
            raise

    def verify_session(self, session_token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify session token and return username if valid.
        
        Returns:
            Tuple of (is_valid: bool, username: str or None)
        """
        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute(
                            """
                            SELECT u.username FROM sessions s
                            JOIN users u ON s.user_id = u.id
                            WHERE s.session_token = %s AND s.expires_at > %s AND u.is_active = TRUE
                            """,
                            (session_token, datetime.now()),
                        )
                        result = c.fetchone()
                if result:
                    return True, result[0]
                return False, None

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                """SELECT u.username FROM sessions s 
                   JOIN users u ON s.user_id = u.id 
                   WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = 1""",
                (session_token, datetime.now()),
            )
            result = c.fetchone()
            conn.close()

            if result:
                return True, result[0]
            return False, None

        except Exception as e:
            logger.error(f"❌ Session verification error: {e}")
            return False, None

    def logout_user(self, session_token: str) -> bool:
        """Invalidate user session."""
        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute("DELETE FROM sessions WHERE session_token = %s", (session_token,))
                    conn.commit()
                logger.info("✅ User logged out successfully")
                return True
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
            conn.close()
            logger.info("✅ User logged out successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username."""
        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute(
                            "SELECT id, username, email, created_at FROM users WHERE username = %s",
                            (username,),
                        )
                        result = c.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "username": result[1],
                        "email": result[2],
                        "created_at": result[3],
                    }
                return None

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "SELECT id, username, email, created_at FROM users WHERE username = ?",
                (username,),
            )
            result = c.fetchone()
            conn.close()

            if result:
                return {
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "created_at": result[3],
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching user info: {e}")
            return None

    def change_password(
        self, username: str, old_password: str, new_password: str
    ) -> Tuple[bool, str]:
        """Allow user to change password."""
        if not self._validate_password(new_password):
            return False, "❌ New password must be at least 8 characters with uppercase, lowercase, and numbers"

        try:
            if USE_POSTGRES and psycopg is not None:
                with psycopg.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
                        result = c.fetchone()
                        if not result:
                            return False, "❌ User not found"
                        user_id, password_hash = result
                        if isinstance(password_hash, str):
                            password_hash_bytes = password_hash.encode()
                        else:
                            password_hash_bytes = password_hash
                        if not bcrypt.checkpw(old_password.encode(), password_hash_bytes):
                            return False, "❌ Current password is incorrect"
                        new_password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12)).decode()
                        c.execute(
                            "UPDATE users SET password_hash = %s, updated_at = %s WHERE id = %s",
                            (new_password_hash, datetime.now(), user_id),
                        )
                        conn.commit()
                    logger.info(f"✅ Password changed for user: {username}")
                    return True, "✅ Password changed successfully"

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            result = c.fetchone()

            if not result:
                return False, "❌ User not found"

            user_id, password_hash = result

            # Verify old password
            if not bcrypt.checkpw(old_password.encode(), password_hash):
                return False, "❌ Current password is incorrect"

            # Hash and update new password
            new_password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12))
            c.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (new_password_hash, datetime.now(), user_id),
            )
            conn.commit()
            conn.close()

            logger.info(f"✅ Password changed for user: {username}")
            return True, "✅ Password changed successfully"

        except Exception as e:
            logger.error(f"❌ Password change error: {e}")
            return False, f"❌ Password change error: {str(e)}"

    @staticmethod
    def _validate_password(password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True

    def _ensure_demo_user(self) -> None:
        """Ensure demo account exists for testing."""
        try:
            # Check if demo user already exists
            demo_user_info = self.get_user_info("demo")
            if demo_user_info:
                return  # Demo user already exists
            
            # Create demo user with fixed credentials
            demo_username = "demo"
            demo_email = "demo@research-bot.local"
            demo_password = "Demo123456"
            
            # Register demo user silently
            success, _ = self.register_user(demo_username, demo_email, demo_password)
            if success:
                logger.info("✅ Demo account created successfully")
            else:
                # Demo account might already exist, which is fine
                logger.info("✅ Demo account already exists or is ready")
        except Exception as e:
            logger.warning(f"⚠️ Could not ensure demo user: {e}")


# Singleton instance for app-wide use
_auth_manager = None


def get_auth_manager() -> AuthenticationManager:
    """Get or create authentication manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager
