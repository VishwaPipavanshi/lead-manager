from functools import lru_cache

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_name: str = "Lead Manager API"
    mongodb_url: SecretStr
    database_name: str = "lead_manager"
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=60)
    allowed_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    @field_validator("jwt_algorithm")
    @classmethod
    def require_hs256(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("JWT_ALGORITHM must be HS256.")
        return value

    @model_validator(mode="after")
    def validate_secrets_and_origins(self) -> "Settings":
        secret = self.jwt_secret_key.get_secret_value()
        if secret.startswith("REPLACE_WITH_"):
            raise ValueError("JWT_SECRET_KEY must be configured with a random secret.")
        if len(secret) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters.")
        if "YOUR_CLUSTER" in self.mongodb_url.get_secret_value():
            raise ValueError("MONGODB_URL must be configured with a MongoDB connection URI.")
        if self.app_env.lower() == "production" and any(
            "localhost" in origin or origin == "*" for origin in self.cors_origins
        ):
            raise ValueError("Production CORS origins must be explicit public origins.")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
