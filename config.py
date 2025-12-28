# config.py
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
VECTOR_DB_DIR = BASE_DIR / "vector_db"
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://capstone:capstone@localhost:5433/capstone_db",
)
EXPORT_DIR = BASE_DIR / "exports"
LOG_PATH = BASE_DIR / "logs" / "app.log"

for dir_path in [UPLOAD_DIR, VECTOR_DB_DIR, EXPORT_DIR, BASE_DIR / "db", BASE_DIR / "logs"]:
    dir_path.mkdir(parents=True, exist_ok=True)

# LLM and Embeddings
# Default model for local development on CPU machines — change as needed.
OLLAMA_MODEL = "gemma3"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# Database backend toggle
USE_POSTGRES = True

# APIs (optional)
SEMANTIC_SCHOLAR_API_KEY = None

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)