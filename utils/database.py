# utils/database.py
from typing import List, Tuple
from config import DB_PATH, DATABASE_URL, USE_POSTGRES, logger

try:
    import psycopg
except Exception:
    psycopg = None

def init_db() -> None:
    """Initialize the database (Postgres preferred, fallback to SQLite)."""
    if USE_POSTGRES and psycopg is not None:
        try:
            with psycopg.connect(DATABASE_URL) as conn:
                with conn.cursor() as c:
                    c.execute(
                        """
                        CREATE TABLE IF NOT EXISTS references_tbl (
                            id SERIAL PRIMARY KEY,
                            title TEXT,
                            authors TEXT,
                            year TEXT,
                            doi TEXT,
                            bibtex TEXT
                        )
                        """
                    )
                    c.execute(
                        """
                        CREATE TABLE IF NOT EXISTS notes (
                            id SERIAL PRIMARY KEY,
                            content TEXT,
                            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                conn.commit()
            logger.info("PostgreSQL DB initialized")
            return
        except Exception as e:
            logger.error(f"PostgreSQL init error: {e}. Falling back to SQLite.")

    # Fallback: SQLite
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS references_tbl
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, authors TEXT, year TEXT, doi TEXT, bibtex TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS notes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        logger.info("SQLite DB initialized")
    except Exception as e:
        logger.error(f"SQLite init error: {e}")
    finally:
        conn.close()

def add_reference(title: str, authors: str, year: str, doi: str, bibtex: str, user_id: int = None) -> None:
    """Add reference to DB (Postgres preferred). If user_id provided, associates with that user."""
    if USE_POSTGRES and psycopg is not None:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as c:
                if user_id is not None:
                    c.execute(
                        "INSERT INTO references_tbl (title, authors, year, doi, bibtex, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        (title, authors, year, doi, bibtex, user_id),
                    )
                else:
                    c.execute(
                        "INSERT INTO references_tbl (title, authors, year, doi, bibtex) VALUES (%s, %s, %s, %s, %s)",
                        (title, authors, year, doi, bibtex),
                    )
            conn.commit()
        logger.info(f"Added reference (Postgres): {title}")
        return

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id is not None:
        c.execute("INSERT INTO references_tbl (title, authors, year, doi, bibtex, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (title, authors, year, doi, bibtex, user_id))
    else:
        c.execute("INSERT INTO references_tbl (title, authors, year, doi, bibtex) VALUES (?, ?, ?, ?, ?)",
                  (title, authors, year, doi, bibtex))
    conn.commit()
    conn.close()
    logger.info(f"Added reference (SQLite): {title}")

def get_references(user_id: int = None) -> List[Tuple]:
    """Get all references. If user_id provided, returns only that user's references."""
    if USE_POSTGRES and psycopg is not None:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as c:
                if user_id is not None:
                    c.execute(
                        "SELECT id, title, authors, year, doi, bibtex FROM references_tbl WHERE user_id = %s OR user_id IS NULL",
                        (user_id,)
                    )
                else:
                    c.execute("SELECT id, title, authors, year, doi, bibtex FROM references_tbl")
                return [
                    {"id": row[0], "title": row[1], "authors": row[2], "year": row[3], "doi": row[4], "bibtex": row[5]}
                    for row in c.fetchall()
                ]

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id is not None:
        c.execute(
            "SELECT id, title, authors, year, doi, bibtex FROM references_tbl WHERE user_id = ? OR user_id IS NULL",
            (user_id,)
        )
    else:
        c.execute("SELECT id, title, authors, year, doi, bibtex FROM references_tbl")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": row[0], "title": row[1], "authors": row[2], "year": row[3], "doi": row[4], "bibtex": row[5]}
        for row in rows
    ]

# Similar for notes if expanded