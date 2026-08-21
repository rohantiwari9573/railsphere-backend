import hashlib
import hmac

from cryptography.fernet import Fernet
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.core.config import settings


def _fernet() -> Fernet:
    if not settings.DATA_ENCRYPTION_KEY:
        raise RuntimeError(
            "DATA_ENCRYPTION_KEY is not set -- required to read/write "
            "encrypted columns. Generate one with: "
            'python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        )
    return Fernet(settings.DATA_ENCRYPTION_KEY.encode())


class EncryptedString(TypeDecorator):
    """
    Transparently encrypts a string column at rest with Fernet
    (AES-128-CBC + HMAC, random IV per value). Application code always
    sees plaintext -- encryption/decryption happens at the SQLAlchemy
    binding layer, so nothing above the model needs to change.

    Deliberately not fail-open like the Redis cache: a missing key
    means the app can't handle this data confidentially at all, so it
    should error loudly rather than silently store or return plaintext.
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return _fernet().encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return _fernet().decrypt(value.encode()).decode()


def blind_index(value: str) -> str:
    """
    Deterministic HMAC-SHA256 of a normalized value, used as a lookup
    index for encrypted columns. Fernet ciphertext is randomized (new
    IV every call), so equality search (e.g. login-by-email) has to go
    through this index instead of the encrypted column itself.
    """
    if not settings.DATA_ENCRYPTION_KEY:
        raise RuntimeError("DATA_ENCRYPTION_KEY is not set.")
    hmac_key = hashlib.sha256(settings.DATA_ENCRYPTION_KEY.encode()).digest()
    normalized = value.strip().lower()
    return hmac.new(hmac_key, normalized.encode(), hashlib.sha256).hexdigest()
