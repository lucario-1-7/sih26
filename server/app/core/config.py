from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", REPO_ROOT_ENV_FILE), extra="ignore"
    )

    ENVIRONMENT: str = "development"

    # PRESENTATION-ONLY demo/bypass login (see app/services/auth_service.py
    # DEMO_PERSONAS / demo_login). ON by default for this presentation build
    # so it doesn't need an env var to be set. Never activates because a
    # real provider (MSG91) failed — it is a completely separate, explicit
    # opt-in path, not a fallback. Force-disabled in production regardless of
    # what's in the environment — see the validator below — so a stray
    # DEMO_MODE=true left in a prod .env can never actually take effect.
    DEMO_MODE: bool = True

    @model_validator(mode="after")
    def _demo_mode_never_in_production(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.DEMO_MODE:
            self.DEMO_MODE = False
        return self

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
    # Minimum time between two OTP requests for the same phone — resend abuse
    # protection independent of MSG91's own delivery-side throttling.
    OTP_RESEND_COOLDOWN_SECONDS: int = 30

    # MSG91 OTP Widget (production OTP provider — see app/services/otp_msg91.py).
    # MSG91's Widget product generates and verifies the OTP itself: WIDGET_ID
    # identifies the widget configured in the MSG91 dashboard, TOKEN_AUTH is
    # that widget's own auth token (Widget config page -> "Server-Side
    # Integration" -> Token Auth — NOT the account-level Auth Key). All blank
    # by default so a missing production config fails loudly rather than
    # silently falling back to console logging. Never given a real default
    # value here — see .env.example for the placeholder shape and setup steps.
    MSG91_WIDGET_ID: str | None = None
    MSG91_TOKEN_AUTH: str | None = None
    # Account-level key. Not used by the Widget send/verify calls (those use
    # WIDGET_ID/TOKEN_AUTH only) — kept for any other MSG91 API this project
    # may need later (e.g. verifyAccessToken for a future client-widget flow).
    MSG91_AUTH_KEY: str | None = None
    MSG91_BASE_URL: str = "https://control.msg91.com/api/v5/widget"
    MSG91_TIMEOUT_SECONDS: float = 10.0

    ML_SERVICE_URL: str = Field(default="http://localhost:8001")
    ML_SERVICE_TIMEOUT_SECONDS: float = 10.0

    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.82
    DUPLICATE_CANDIDATE_LIMIT: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
