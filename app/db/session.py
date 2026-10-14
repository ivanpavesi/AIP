"""Connessioni lazy: importare l'app non contatta alcun database."""
from functools import lru_cache
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import get_settings


@lru_cache
def get_engine():
    url = get_settings().database_url
    if url is None:
        raise RuntimeError("Configurare AIP_DATABASE_URL prima di usare il database.")
    return create_engine(url.get_secret_value(), pool_pre_ping=True, echo=False, hide_parameters=True)


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
