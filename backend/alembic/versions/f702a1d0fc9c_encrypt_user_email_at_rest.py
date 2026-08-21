"""encrypt user email at rest

Revision ID: f702a1d0fc9c
Revises: 3e20ff7c0a5a
Create Date: 2026-08-21 14:56:41.918873

"""
import hashlib
import hmac
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from cryptography.fernet import Fernet

from app.core.config import settings


# revision identifiers, used by Alembic.
revision: str = 'f702a1d0fc9c'
down_revision: Union[str, Sequence[str], None] = '3e20ff7c0a5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _require_key() -> str:
    if not settings.DATA_ENCRYPTION_KEY:
        raise RuntimeError(
            "DATA_ENCRYPTION_KEY must be set to run this migration -- "
            "it encrypts existing plaintext emails in place. Generate "
            'one with: python -c "from cryptography.fernet import '
            'Fernet; print(Fernet.generate_key().decode())"'
        )
    return settings.DATA_ENCRYPTION_KEY


def upgrade() -> None:
    """
    Encrypts users.email in place with Fernet and adds email_index, a
    deterministic HMAC-SHA256 of the normalized email used for
    equality lookups (login-by-email, uniqueness) now that the email
    column itself holds randomized ciphertext. See
    app/core/encryption.py for the runtime side of this.
    """
    key = _require_key()
    fernet = Fernet(key.encode())
    hmac_key = hashlib.sha256(key.encode()).digest()

    op.add_column(
        "users", sa.Column("email_index", sa.String(length=64), nullable=True)
    )
    op.alter_column(
        "users", "email", existing_type=sa.String(length=255),
        type_=sa.String(length=500),
    )

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, email FROM users")).fetchall()
    for row in rows:
        plaintext = row.email
        ciphertext = fernet.encrypt(plaintext.encode()).decode()
        index = hmac.new(
            hmac_key, plaintext.strip().lower().encode(), hashlib.sha256
        ).hexdigest()
        conn.execute(
            sa.text(
                "UPDATE users SET email = :email, email_index = :idx "
                "WHERE id = :id"
            ),
            {"email": ciphertext, "idx": index, "id": row.id},
        )

    op.drop_index("ix_users_email", table_name="users")
    op.alter_column("users", "email_index", nullable=False)
    op.create_index(
        "ix_users_email_index", "users", ["email_index"], unique=True
    )


def downgrade() -> None:
    """
    Decrypts users.email back to plaintext and drops email_index.
    """
    key = _require_key()
    fernet = Fernet(key.encode())

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, email FROM users")).fetchall()
    for row in rows:
        plaintext = fernet.decrypt(row.email.encode()).decode()
        conn.execute(
            sa.text("UPDATE users SET email = :email WHERE id = :id"),
            {"email": plaintext, "id": row.id},
        )

    op.drop_index("ix_users_email_index", table_name="users")
    op.drop_column("users", "email_index")
    op.alter_column(
        "users", "email", existing_type=sa.String(length=500),
        type_=sa.String(length=255),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
