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
    LLM_API_KEY: Optional[str] = "your_groq_api_key_here"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # Backward compatibility fields
    OPENAI_API_KEY: Optional[str] = "your_openai_api_key_here"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    @property
    def effective_api_key(self) -> str:
        """Returns the active LLM API key, prioritizing LLM_API_KEY over OPENAI_API_KEY."""
        if self.LLM_API_KEY and not any(x in self.LLM_API_KEY.lower() for x in ["your_", "placeholder", "groq_api_key"]):
            return self.LLM_API_KEY
        if self.OPENAI_API_KEY and not any(x in self.OPENAI_API_KEY.lower() for x in ["your_", "placeholder", "openai_api_key"]):
            return self.OPENAI_API_KEY
        return self.LLM_API_KEY or self.OPENAI_API_KEY or ""

    @property
    def effective_model(self) -> str:
        """Returns the active LLM model name."""
        if self.LLM_MODEL and self.LLM_MODEL != "llama-3.3-70b-versatile":
            return self.LLM_MODEL
        if self.OPENAI_MODEL and self.OPENAI_MODEL != "gpt-4o-mini":
            return self.OPENAI_MODEL
        return self.LLM_MODEL or self.OPENAI_MODEL

    # Scraper & Scheduler settings
    SCRAPING_INTERVAL_MINUTES: int = 60
    CRON_SECRET: Optional[str] = "default_cron_secret"

settings = Settings()
