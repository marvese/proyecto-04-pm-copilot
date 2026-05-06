"""add users table

Revision ID: 002
Revises: 001
Create Date: 2026-05-06

"""
from __future__ import annotations

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email            TEXT NOT NULL,
            hashed_password  TEXT NOT NULL,
            role             VARCHAR(16) NOT NULL DEFAULT 'user'
                                 CHECK (role IN ('admin', 'user')),
            is_active        BOOLEAN NOT NULL DEFAULT true,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users (email)")
    op.execute("""
        CREATE TRIGGER set_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS users CASCADE")
