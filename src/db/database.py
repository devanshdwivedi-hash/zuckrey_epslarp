import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings

logger = logging.getLogger("autonomous_agent.db.database")

# Detect engine configuration based on DATABASE_URL
database_url = settings.DATABASE_URL

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.DEBUG,
}

import os

is_vercel = "VERCEL" in os.environ

if database_url.startswith("sqlite"):
    # SQLite: disable same-thread restriction for async compat
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL / Supabase / Neon: use connection pool sizing suitable for cloud & serverless
    if is_vercel:
        from sqlalchemy.pool import NullPool
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    connect_args=connect_args,
    **engine_kwargs
)

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def init_db():
    """
    Initializes database schema tables.
    Importing models ensures Base metadata registers all mapped tables before
    calling create_all, which is a no-op if tables already exist.
    """
    import src.db.models  # noqa: F401
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def get_db():
    """
    FastAPI dependency that provides a transactional database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Utility to verify the database connection is reachable.
    Returns True if connected, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
