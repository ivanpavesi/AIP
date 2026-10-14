"""Configurazione Pydantic: segreti solo da ambiente o dal file .env ignorato da Git."""
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIP_", env_file=".env", extra="ignore", hide_input_in_errors=True)

    environment: Literal["development", "test", "production"] = "development"
    database_url: SecretStr | None = None
    encryption_key: SecretStr | None = None
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "[::1]"]

    @field_validator("database_url", "encryption_key", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        return None if value == "" else value

    @field_validator("database_url")
    @classmethod
    def require_postgresql(cls, value):
        if value is not None:
            try:
                url = make_url(value.get_secret_value())
                valid = url.drivername == "postgresql+psycopg"
            except Exception:
                valid = False
            if not valid:
                raise ValueError("Usare un URL PostgreSQL con driver postgresql+psycopg.")
        return value

    @field_validator("allowed_hosts")
    @classmethod
    def validate_hosts(cls, value):
        if not value or "*" in value:
            raise ValueError("Specificare gli host consentiti senza wildcard globale.")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
