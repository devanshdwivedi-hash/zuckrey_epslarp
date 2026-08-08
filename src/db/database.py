"""
database.py

Establishes the SQLAlchemy engine, session factory, and FastAPI dependency
used across the application. Supports two modes:

  1. Local development: SQLite file database (default), with
     `check_same_thread=False` so the connection can be shared safely across
     FastAPI's threaded request handling.
  2. Production: PostgreSQL, configured via the `DATABASE_URL` environment
     variable. Handles normalization of the legacy `postgres://` scheme
     (still emitted by some hosting providers, e.g. Heroku/Render) to the
     `postgresql://` scheme that SQLAlchemy/psycopg2 expect.

Requires `psycopg2-binary` (or `psycopg`) to be installed for the
PostgreSQL code path — see requirements.txt.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Connection URL resolution
# ---------------------------------------------------------------------------

DEFAULT_SQLITE_URL = "sqlite:///./app.db"

RAW_DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE_URL)


def _normalize_database_url(url: str) -> str:
    """Normalize legacy `postgres://` URLs to the `postgresql://` scheme.

    Some managed Postgres providers still hand out connection strings that
    start with `postgres://`, which SQLAlchemy (via psycopg2) no longer
    accepts directly. This rewrites the scheme in place while leaving every
    other part of the URL untouched.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = _normalize_database_url(RAW_DATABASE_URL)

# ---------------------------------------------------------------------------
# Engine configuration
# ---------------------------------------------------------------------------

_is_sqlite = DATABASE_URL.startswith("sqlite")

_engine_kwargs = {}
if _is_sqlite:
    # SQLite only allows the connection to be used in the thread that
    # created it by default. FastAPI/Starlette may hand requests off to
    # different worker threads, so this needs to be disabled for local dev.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Reasonable production defaults for PostgreSQL. `pool_pre_ping` avoids
    # handing out stale/dead connections after periods of idleness.
    _engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **_engine_kwargs)

# ---------------------------------------------------------------------------
# Session factory + FastAPI dependency
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a database session and guarantees
    it is closed after the request finishes, even if an exception occurs.

    Usage:
        @app.get("/posts")
        def list_posts(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
