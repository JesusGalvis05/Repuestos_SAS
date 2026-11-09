from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://jg:local-only@localhost:5432/jg_repuestos"
    jwt_secret: SecretStr
    jwt_issuer: str = "jg-repuestos"
    jwt_audience: str = "jg-web"
    access_token_minutes: int = Field(default=10, ge=1, le=30)
    refresh_token_days: int = Field(default=7, ge=1, le=30)
    cookie_secure: bool = True
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]
    login_max_attempts: int = Field(default=5, ge=2)
    login_lock_minutes: int = Field(default=15, ge=1)
    frontend_dist: Path | None = None

    @model_validator(mode="after")
    def validate_security(self):
        secret = self.jwt_secret.get_secret_value()
        if len(secret) < 32 or secret.lower().startswith(("change", "replace", "cambiar")):
            raise ValueError("JWT_SECRET debe ser un secreto aleatorio de al menos 32 caracteres")
        if not self.database_url.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL debe usar PostgreSQL con psycopg")
        if self.app_env == "production" and (
            not self.cookie_secure
            or any(not o.startswith("https://") for o in self.allowed_origins)
        ):
            raise ValueError("Producción requiere cookies seguras y orígenes HTTPS")
        if "*" in self.allowed_origins:
            raise ValueError("CORS no permite orígenes comodín")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
