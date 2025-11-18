# utils/database.py
import sqlite3
from typing import List, Tuple
from config import DB_PATH, logger

def init_db() -> None:
    """Initialize SQLite DB."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS references
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, authors TEXT, year TEXT, doi TEXT, bibtex TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS notes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
    except Exception as e:
        logger.error(f"DB init error: {e}")
    finally:
        conn.close()

def add_reference(title: str, authors: str, year: str, doi: str, bibtex: str) -> None:
    """Add reference to DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO references (title, authors, year, doi, bibtex) VALUES (?, ?, ?, ?, ?)",
              (title, authors, year, doi, bibtex))
    conn.commit()
    conn.close()
    logger.info(f"Added reference: {title}")

def get_references() -> List[Tuple]:
    """Get all references."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM references")
    refs = c.fetchall()
    conn.close()
    return refs

# Similar for notes if expanded