import pytest
from cryptography.fernet import Fernet
from app.security.encryption import DataCipher, DecryptionError, EncryptionConfigurationError, get_cipher
from app.db.types import EncryptedText


def test_unicode_roundtrip_and_randomized_ciphertext():
    cipher = DataCipher(Fernet.generate_key().decode())
    plaintext = "Dato sintetico: città, Unicode ✓"
    first, second = cipher.encrypt(plaintext), cipher.encrypt(plaintext)
    assert first != second
    assert plaintext.encode() not in first
    assert cipher.decrypt(first) == plaintext


def test_wrong_key_and_tampering_are_rejected():
    cipher = DataCipher(Fernet.generate_key().decode())
    token = cipher.encrypt("Esempio sintetico")
    other = DataCipher(Fernet.generate_key().decode())
    with pytest.raises(DecryptionError):
        other.decrypt(token)
    with pytest.raises(DecryptionError):
        cipher.decrypt(token[:-10] + b"altered")


@pytest.mark.parametrize("key", ["", "invalid-key", "non-ascii-è"])
def test_invalid_keys(key):
    with pytest.raises(EncryptionConfigurationError):
        DataCipher(key)


def test_missing_key_fails_closed():
    with pytest.raises(EncryptionConfigurationError):
        get_cipher()
    with pytest.raises(EncryptionConfigurationError):
        EncryptedText().process_bind_param("Sintetico", None)


def test_sqlalchemy_type_encrypts_and_decrypts(monkeypatch):
    monkeypatch.setenv("AIP_ENCRYPTION_KEY", Fernet.generate_key().decode())
    datatype = EncryptedText()
    encrypted = datatype.process_bind_param("Nome sintetico", None)
    assert isinstance(encrypted, bytes)
    assert datatype.process_result_value(encrypted, None) == "Nome sintetico"
    assert datatype.process_bind_param(None, None) is None
    assert datatype.process_result_value(None, None) is None
