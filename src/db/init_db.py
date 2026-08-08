"""
Standalone database initialization script.

Usage:
    python -m src.db.init_db

Run this once locally before deploying to Vercel / Railway / Render to
create all physical tables in Supabase (or any configured PostgreSQL database).
It is safe to run multiple times — SQLAlchemy's create_all() is idempotent
and will NOT drop or alter existing tables.
"""
import logging
import sys
import os

# Allow running from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("init_db")


def main():
    logger.info("=== Autonomous Agent — Database Initialization ===")

    # Import after path setup to ensure settings loads correctly
    from src.db.database import engine, Base, check_db_connection
    import src.db.models  # noqa: F401 — registers all ORM models with Base

    # Step 1: Verify connection
    logger.info("Step 1/3 — Verifying database connection...")
    if not check_db_connection():
        logger.error("Cannot reach the database. Check DATABASE_URL in .env and try again.")
        sys.exit(1)
    logger.info("Connection OK.")

    # Step 2: Create all tables
    logger.info("Step 2/3 — Creating tables (create_all — idempotent)...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created (or already exist).")

    # Step 3: Report created tables
    logger.info("Step 3/3 — Tables registered in metadata:")
    for table_name in Base.metadata.tables.keys():
        logger.info(f"  ✓ {table_name}")

    logger.info("=== Initialization complete. Database is ready. ===")


if __name__ == "__main__":
    main()
