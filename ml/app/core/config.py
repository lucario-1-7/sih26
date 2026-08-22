from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", REPO_ROOT_ENV_FILE), extra="ignore")

    ML_MODEL_NAME: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384
    DEFAULT_DUPLICATE_THRESHOLD: float = 0.82


@lru_cache
def get_settings() -> Settings:
    return Settings()
