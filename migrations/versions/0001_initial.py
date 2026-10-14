"""Modelli iniziali con identità e contenuto clinico in schemi distinti."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.schema.CreateSchema("identity_data"))
    op.execute(sa.schema.CreateSchema("clinical_data"))
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("email", sa.LargeBinary(), nullable=False),
        sa.Column("display_name", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('therapist', 'researcher', 'administrator')", name=op.f("ck_users_valid_role")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_table(
        "patient_identities",
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.LargeBinary(), nullable=False),
        sa.Column("contact_details", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("patient_id", name=op.f("pk_patient_identities")),
        schema="identity_data",
    )
    op.create_table(
        "clinical_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["identity_data.patient_identities.patient_id"], ondelete="RESTRICT", name=op.f("fk_clinical_records_patient_id_patient_identities")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT", name=op.f("fk_clinical_records_created_by_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clinical_records")), schema="clinical_data",
    )
    op.create_index(op.f("ix_clinical_data_clinical_records_patient_id"), "clinical_records", ["patient_id"], schema="clinical_data")
    op.create_index(op.f("ix_clinical_data_clinical_records_created_by"), "clinical_records", ["created_by"], schema="clinical_data")
    # Nessun accesso implicito a PUBLIC negli schemi sensibili.
    op.execute("REVOKE ALL ON SCHEMA identity_data, clinical_data FROM PUBLIC")
    op.execute("REVOKE ALL ON TABLE users, identity_data.patient_identities, clinical_data.clinical_records FROM PUBLIC")


def downgrade():
    # Usare solo su database locali vuoti o dopo aver valutato la perdita di dati.
    op.drop_table("clinical_records", schema="clinical_data")
    op.drop_table("patient_identities", schema="identity_data")
    op.drop_table("users")
    op.execute(sa.schema.DropSchema("clinical_data"))
    op.execute(sa.schema.DropSchema("identity_data"))
