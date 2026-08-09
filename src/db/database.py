import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings

logger = logging.getLogger("autonomous_agent.db.database")

is_vercel = "VERCEL" in os.environ

# Detect engine configuration based on formatted_database_url
database_url = settings.formatted_database_url

# On Vercel serverless runtime, SQLite must write to /tmp directory because root filesystem is read-only
if is_vercel and database_url.startswith("sqlite:///./"):
    database_url = "sqlite:////tmp/autonomous_agent.db"

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": settings.DEBUG,
}

if database_url.startswith("sqlite"):
    # SQLite: disable same-thread restriction for async compatibility
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL / Supabase / Neon: use connection pool settings suitable for cloud & serverless
    if is_vercel:
        from sqlalchemy.pool import NullPool
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

# Create SQLAlchemy engine safely
try:
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        **engine_kwargs
    )
except Exception as engine_err:
    logger.error(f"Failed to create SQLAlchemy engine with URL '{database_url}': {engine_err}")
    fallback_path = "/tmp/fallback_autonomous.db" if is_vercel else "./fallback_autonomous.db"
    engine = create_engine(f"sqlite:///{fallback_path}", connect_args={"check_same_thread": False})

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()

_db_initialized = False


def init_db():
    """
    Initializes database schema tables automatically on app initialization.
    Importing models ensures Base metadata registers all mapped tables before create_all.
    Wrapped in try/except so database connection issues or missing variables fail gracefully.
    """
    global _db_initialized
    try:
        import src.db.models  # noqa: F401
        from src.db.models import PublishedPost
        from datetime import datetime

        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        _db_initialized = True
        logger.info("Database tables initialized successfully.")

        # Seed initial post if database is empty to prevent empty feed state
        db = SessionLocal()
        try:
            if db.query(PublishedPost).count() == 0:
                logger.info("Database is empty. Seeding initial technical post...")
                seed_post = PublishedPost(
                    title="Technical Deep Dive: Mitigating Prompt Injection Attacks with a Layered Defense Strategy",
                    content="Technical Deep Dive: Mitigating prompt injection attacks with a layered defense strategy. Autonomous AI agent security requires strict control flow scoping, non-executable prompt sandboxing, and output validation.",
                    selection_reason="Selected due to high technical relevance to AI Security.",
                    why_relevant_now="Critical vulnerability pattern affecting LLM-powered agent workflows in production.",
                    sources=["https://security.googleblog.com"],
                    source_url="https://security.googleblog.com",
                    source_name="Google Security Blog",
                    persona_name="Zuckrey Infiltrator",
                    score=9.5,
                    created_at=datetime.utcnow(),
                    timestamp=datetime.utcnow(),
                    article_published_at=datetime.utcnow()
                )
                db.add(seed_post)
                db.commit()
                logger.info("Initial seed post committed successfully.")
        except Exception as seed_err:
            db.rollback()
            logger.warning(f"Notice seeding initial post (handled gracefully): {seed_err}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Database initialization error (handled gracefully): {e}")


def ensure_db_initialized():
    """
    Guarantees database tables exist before executing any queries.
    """
    global _db_initialized
    if not _db_initialized:
        init_db()


def get_db():
    """
    FastAPI dependency that provides a transactional database session per request.
    Ensures tables exist before returning the session.
    """
    ensure_db_initialized()
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
