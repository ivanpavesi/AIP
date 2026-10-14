"""Cifratura autenticata Fernet. La chiave viene fornita dall'esterno.

La perdita della chiave rende i dati illeggibili. Non registrare mai chiave,
contenuto o token nei log. La rotazione delle chiavi sarà progettata prima dell'uso clinico.
"""
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class EncryptionConfigurationError(RuntimeError):
    """La cifratura è stata richiesta senza una chiave valida."""


class DecryptionError(ValueError):
    """Token alterato, chiave errata o contenuto non valido."""


class DataCipher:
    def __init__(self, key: str):
        try:
            self._fernet = Fernet(key.encode("ascii"))
        except (ValueError, UnicodeError) as exc:
            raise EncryptionConfigurationError("Chiave di cifratura non valida.") from exc

    def encrypt(self, plaintext: str) -> bytes:
        return self._fernet.encrypt(plaintext.encode("utf-8"))

    def decrypt(self, ciphertext: bytes) -> str:
        try:
            return self._fernet.decrypt(ciphertext).decode("utf-8")
        except (InvalidToken, UnicodeError) as exc:
            raise DecryptionError("Impossibile decifrare il dato.") from exc


def get_cipher() -> DataCipher:
    key = get_settings().encryption_key
    if key is None:
        raise EncryptionConfigurationError("Configurare AIP_ENCRYPTION_KEY prima di usare dati sensibili.")
    return DataCipher(key.get_secret_value())
