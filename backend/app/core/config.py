from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    app_env: str = "development"
    database_url: str = Field(default="", repr=False)
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_user: str | None = None
    postgres_password: SecretStr | None = None
    postgres_db: str | None = None
    docker_runtime: bool = False
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
        if not self.database_url:
            if not self.postgres_user or not self.postgres_password or not self.postgres_db:
                raise ValueError("Configure DATABASE_URL o POSTGRES_USER/PASSWORD/DB")
            self.database_url = URL.create(
                "postgresql+psycopg",
                username=self.postgres_user,
                password=self.postgres_password.get_secret_value(),
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_db,
            ).render_as_string(hide_password=False)
        secret = self.jwt_secret.get_secret_value()
        if len(secret) < 32 or secret.lower().startswith(("change", "replace", "cambiar")):
            raise ValueError("JWT_SECRET debe ser un secreto aleatorio de al menos 32 caracteres")
        if not self.database_url.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL debe usar PostgreSQL con psycopg")
        address = make_url(self.database_url)
        if self.docker_runtime and (address.host != "db" or address.port != 5432):
            raise ValueError("Docker requiere PostgreSQL exclusivamente en db:5432")
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
