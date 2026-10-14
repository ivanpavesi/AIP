"""Test su un database PostgreSQL esclusivamente locale e sacrificabile.

Impostare AIP_TEST_DATABASE_URL con un database vuoto il cui nome termina in _test.
Il test crea e rimuove lo schema AIP: non usare database contenenti dati da conservare.
"""
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import ClinicalRecord, PatientIdentity, User
from app.db.session import get_engine

pytestmark = pytest.mark.postgres


@pytest.fixture
def local_database(monkeypatch):
    raw = os.environ.get("AIP_TEST_DATABASE_URL")
    if not raw:
        pytest.skip("AIP_TEST_DATABASE_URL non configurato; eseguire su PostgreSQL locale usa e getta.")
    url = make_url(raw)
    host = url.query.get("host", url.host)
    socket_is_local = isinstance(host, str) and host.startswith("/") and Path(host).is_relative_to(Path.cwd() / ".local")
    if host not in ("localhost", "127.0.0.1", "::1") and not socket_is_local:
        pytest.fail("I test rifiutano database remoti.")
    if not url.database or not url.database.endswith("_test"):
        pytest.fail("Il nome del database deve terminare in _test.")
    engine = create_engine(url, hide_parameters=True)
    with engine.connect() as connection:
        if inspect(connection).get_table_names() or any(s in inspect(connection).get_schema_names() for s in ("identity_data", "clinical_data")):
            pytest.fail("Il database di test deve essere vuoto.")
    monkeypatch.setenv("AIP_DATABASE_URL", raw)
    monkeypatch.setenv("AIP_ENCRYPTION_KEY", Fernet.generate_key().decode())
    get_settings.cache_clear()
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    yield engine, config
    command.downgrade(config, "base")
    with engine.connect() as connection:
        assert "users" not in inspect(connection).get_table_names()
        assert "identity_data" not in inspect(connection).get_schema_names()
        assert "clinical_data" not in inspect(connection).get_schema_names()
    get_engine().dispose()
    engine.dispose()


def test_migration_orm_encryption_constraints_and_downgrade(local_database):
    engine, config = local_database
    # Alembic confronta la migrazione applicata con i modelli SQLAlchemy.
    command.check(config)
    with Session(engine) as session:
        user = User(role="therapist", email="synthetic@example.invalid", display_name="Utente sintetico")
        patient = PatientIdentity(full_name="Persona sintetica", contact_details=None)
        session.add_all([user, patient])
        session.flush()
        record = ClinicalRecord(patient_id=patient.patient_id, created_by=user.id, content="Contenuto sintetico senza dati clinici")
        session.add(record)
        session.commit()
        ids = (user.id, patient.patient_id, record.id)

    with engine.connect() as connection:
        name = connection.execute(text("SELECT full_name FROM identity_data.patient_identities")).scalar_one()
        content = connection.execute(text("SELECT content FROM clinical_data.clinical_records")).scalar_one()
        email = connection.execute(text("SELECT email FROM users")).scalar_one()
        assert isinstance(name, bytes) and b"Persona sintetica" not in name
        assert isinstance(content, bytes) and b"Contenuto sintetico" not in content
        assert b"synthetic@example.invalid" not in email
    with Session(engine) as session:
        assert session.get(PatientIdentity, ids[1]).full_name == "Persona sintetica"
        assert session.get(ClinicalRecord, ids[2]).content == "Contenuto sintetico senza dati clinici"
        session.add(User(role="invalid", email="synthetic@example.invalid", display_name="Sintetico"))
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()
    with engine.begin() as connection:
        with pytest.raises(IntegrityError):
            connection.execute(text("DELETE FROM identity_data.patient_identities"))
