"""Ogni test parte senza credenziali reali e con configurazione isolata."""
import pytest
from fastapi.testclient import TestClient
from app.core.config import Settings, get_settings
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    monkeypatch.delenv("AIP_DATABASE_URL", raising=False)
    monkeypatch.delenv("AIP_ENCRYPTION_KEY", raising=False)
    monkeypatch.setattr(Settings, "model_config", {**Settings.model_config, "env_file": None})
    get_settings.cache_clear()
    get_engine.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()


@pytest.fixture
def client():
    with TestClient(create_app(Settings(allowed_hosts=["testserver"]))) as client:
        yield client
