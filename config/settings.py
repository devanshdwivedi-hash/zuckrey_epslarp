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
    LLM_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    @property
    def effective_api_key(self) -> str:
        """
        Returns the active LLM API key, checking Groq, Grok (xAI), LLM_API_KEY, and OpenAI API keys.
        """
        for key in [self.GROQ_API_KEY, self.GROK_API_KEY, self.LLM_API_KEY, self.OPENAI_API_KEY]:
            if key and not any(x in key.lower() for x in ["your_", "placeholder", "api_key"]):
                return key
        return ""

    @property
    def effective_base_url(self) -> str:
        """
        Auto-detects the provider base URL based on key prefix or environment config.
        """
        key = self.effective_api_key
        if key.startswith("xai-") or self.GROK_API_KEY:
            return "https://api.x.ai/v1"
        if key.startswith("gsk-") or self.GROQ_API_KEY:
            return "https://api.groq.com/openai/v1"
        if key.startswith("sk-") and not key.startswith("gsk-"):
            return "https://api.openai.com/v1"
        return self.LLM_BASE_URL

    @property
    def effective_model(self) -> str:
        """
        Auto-detects active LLM model name based on provider.
        """
        key = self.effective_api_key
        if key.startswith("xai-") or self.GROK_API_KEY:
            return "grok-beta"
        if key.startswith("gsk-") or self.GROQ_API_KEY:
            return "llama-3.3-70b-versatile"
        if key.startswith("sk-") and not key.startswith("gsk-"):
            return "gpt-4o-mini"
        return self.LLM_MODEL

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
