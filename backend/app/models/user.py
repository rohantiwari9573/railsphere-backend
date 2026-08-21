from sqlalchemy import Boolean, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column

from app.core.encryption import EncryptedString, blind_index
from app.db.base import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Encrypted at rest (see app/core/encryption.py) -- application
    # code still just reads/writes plaintext through this attribute,
    # encryption happens transparently at the DB binding layer.
    email: Mapped[str] = mapped_column(
        EncryptedString(500),
        nullable=False,
    )

    # Deterministic HMAC of the (normalized) email, kept in sync by
    # the event listeners below. Fernet ciphertext is randomized, so
    # equality lookups (login-by-email, uniqueness) go through this
    # column instead of `email` itself.
    email_index: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


@event.listens_for(User, "before_insert")
@event.listens_for(User, "before_update")
def _sync_email_index(mapper, connection, target: User) -> None:
    target.email_index = blind_index(target.email)