"""add chat_sessions and chat_messages tables

Revision ID: 003
Revises: 002
Create Date: 2026-05-06
"""
from __future__ import annotations

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_project_id
            ON chat_sessions (project_id)
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID        NOT NULL REFERENCES chat_sessions (id) ON DELETE CASCADE,
            role       VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant')),
            content    TEXT        NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
            ON chat_messages (session_id, created_at)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS chat_messages")
    op.execute("DROP TABLE IF EXISTS chat_sessions")
