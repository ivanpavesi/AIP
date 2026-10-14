"""Tipo SQLAlchemy che cifra automaticamente ogni scrittura di testo sensibile."""
from sqlalchemy import LargeBinary
from sqlalchemy.types import TypeDecorator

from app.security.encryption import get_cipher


class EncryptedText(TypeDecorator[str]):
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else get_cipher().encrypt(value)

    def process_result_value(self, value, dialect):
        return None if value is None else get_cipher().decrypt(value)
