import pytest
from pydantic import ValidationError
from app.core.config import Settings
from app.db.session import get_engine


def test_homepage_configuration_needs_no_secrets():
    settings = Settings()
    assert settings.database_url is None
    assert settings.encryption_key is None
    with pytest.raises(RuntimeError, match="AIP_DATABASE_URL"):
        get_engine()


@pytest.mark.parametrize("url", ["sqlite:///test.db", "postgresql://localhost/aip", "invalid"])
def test_only_explicit_postgresql_driver_allowed(url):
    with pytest.raises(ValidationError):
        Settings(database_url=url)


def test_secret_values_are_redacted():
    settings = Settings(database_url="postgresql+psycopg://localhost/aip", encryption_key="synthetic-secret")
    assert "synthetic-secret" not in repr(settings)
    assert "postgresql+psycopg" not in repr(settings)


def test_empty_env_values_are_optional():
    assert Settings(database_url="", encryption_key="").database_url is None


def test_wildcard_hosts_rejected():
    with pytest.raises(ValidationError):
        Settings(allowed_hosts=["*"])
