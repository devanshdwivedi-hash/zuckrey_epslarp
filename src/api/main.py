import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.db.database import init_db
from src.scheduler.cron import start_scheduler, stop_scheduler
from src.api.routes import router as api_router

logger = logging.getLogger("autonomous_agent.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager. Initializes DB tables and starts background scheduler on boot.
    """
    logger.info("Initializing database schema on startup...")
    init_db()
    
    logger.info("Starting background scheduler...")
    start_scheduler(run_immediately=False)
    
    yield
    
    logger.info("Shutting down background scheduler & API server...")
    stop_scheduler()


app = FastAPI(
    title="Autonomous Content Agent API",
    description="REST API serving accumulated technical security post feed to evaluators.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORSMiddleware with wildcard permissions as required
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints router
app.include_router(api_router)
