from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", REPO_ROOT_ENV_FILE), extra="ignore"
    )

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://sih26:sih26@localhost:5432/sih26_dev"
    )

    REDIS_URL: str = Field(default="redis://localhost:6379")

    SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = "HS256"
    JWT_KEY_ID: str = "v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5

    ML_SERVICE_URL: str = Field(default="http://localhost:8001")
    ML_SERVICE_TIMEOUT_SECONDS: float = 10.0

    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.82
    DUPLICATE_CANDIDATE_LIMIT: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
