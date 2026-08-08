import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database settings
    DATABASE_URL: str = "sqlite:///./autonomous_agent.db"

    # LLM & Embeddings settings
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Scraper & Scheduler settings
    SCRAPING_INTERVAL_MINUTES: int = 60
    CRON_SECRET: Optional[str] = "default_cron_secret_key"

    @property
    def formatted_database_url(self) -> str:
        """
        Converts legacy postgres:// prefixes to postgresql:// for SQLAlchemy & cloud providers.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

settings = Settings()
