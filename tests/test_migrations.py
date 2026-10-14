from io import StringIO
from alembic import command
from alembic.config import Config
from app.db.models import ClinicalRecord, PatientIdentity, User
from app.db.types import EncryptedText


def test_offline_migration_compiles_for_postgresql():
    output = StringIO()
    command.upgrade(Config("alembic.ini", output_buffer=output), "head", sql=True)
    sql = output.getvalue()
    assert "CREATE SCHEMA identity_data" in sql
    assert "CREATE SCHEMA clinical_data" in sql
    assert "BYTEA" in sql
    assert "REVOKE ALL" in sql
    assert "identity_data.patient_identities" in sql


def test_identifying_and_clinical_columns_are_separated_and_encrypted():
    assert PatientIdentity.__table__.schema == "identity_data"
    assert ClinicalRecord.__table__.schema == "clinical_data"
    assert "full_name" not in ClinicalRecord.__table__.columns
    for model, columns in [(User, ["email", "display_name"]), (PatientIdentity, ["full_name", "contact_details"]), (ClinicalRecord, ["content"])]:
        for name in columns:
            assert isinstance(model.__table__.c[name].type, EncryptedText)
