from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables."""

    APP_NAME: str = "Health Planner API"
    DEBUG: bool = True

    API_PREFIX: str = "/api"

    # OpenAI
    OPENAI_API_KEY: str = None
    OPENAI_MODEL: str = "gpt-5-mini"
    OPENAI_TEMPERATURE: float = 0.0

    DATABASE_URL: str = f"sqlite:///database.db"
    DB_ECHO: bool = False

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8000"]

    # Planning
    MAX_PLAN_WEEKS: int = 16
    DEFAULT_PLAN_WEEKS: int = 12

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
