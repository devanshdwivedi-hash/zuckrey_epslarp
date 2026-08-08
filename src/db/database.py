import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings

logger = logging.getLogger("autonomous_agent.db.database")

# Detect engine configuration based on formatted_database_url
database_url = settings.formatted_database_url

connect_args = {}
if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Create SQLAlchemy engine with connection pool pre-ping
engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def init_db():
    """
    Initializes database schema tables automatically on app initialization.
    Importing models ensures Base metadata registers all mapped tables.
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
