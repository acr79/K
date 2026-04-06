from .database import init_db
from .vector_store import init_collections
from .config import DB_PATH, QDRANT_URL


def bootstrap():
    """Initialize all storage layers. Safe to run multiple times."""
    print(f"Initializing K...")
    print(f"  Database : {DB_PATH}")
    print(f"  Vector DB: {QDRANT_URL}")
    init_db()
    init_collections()
    print("K ready.\n")
