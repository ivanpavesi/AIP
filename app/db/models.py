"""Modelli iniziali, senza route di lettura o scrittura.

identity_data contiene l'identità; clinical_data contiene soltanto riferimenti UUID
pseudonimi e testo cifrato. La separazione in schemi consente futuri permessi distinti.
Non è anonimizzazione: chi ha accesso a entrambi gli schemi può collegare i dati.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import EncryptedText


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('therapist', 'researcher', 'administrator')", name="valid_role"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(EncryptedText())
    display_name: Mapped[str] = mapped_column(EncryptedText())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Nessuna password o credenziale fittizia: l'autenticazione è fuori dallo STEP 1.


class PatientIdentity(Base):
    __tablename__ = "patient_identities"
    __table_args__ = {"schema": "identity_data"}

    patient_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(EncryptedText())
    contact_details: Mapped[str | None] = mapped_column(EncryptedText())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClinicalRecord(Base):
    __tablename__ = "clinical_records"
    __table_args__ = {"schema": "clinical_data"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("identity_data.patient_identities.patient_id", ondelete="RESTRICT"), index=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    content: Mapped[str] = mapped_column(EncryptedText())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
