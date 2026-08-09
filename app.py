import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.api.main import app
from src.db.database import init_db, engine, Base, SessionLocal
from src.db.models import Post, PublishedPost

# Ensure database tables exist and seed posts are injected if table is empty
init_db()

__all__ = ["app", "init_db", "engine", "Base", "SessionLocal", "Post", "PublishedPost"]
