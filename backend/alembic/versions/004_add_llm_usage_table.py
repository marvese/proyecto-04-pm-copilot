"""add llm_usage table

Revision ID: 004
Revises: 003
Create Date: 2026-05-06
"""
from __future__ import annotations

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS llm_usage (
            id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            provider      VARCHAR(32) NOT NULL,
            model         VARCHAR(64) NOT NULL,
            task_type     VARCHAR(32) NOT NULL,
            input_tokens  INTEGER     NOT NULL,
            output_tokens INTEGER     NOT NULL,
            cost_usd      NUMERIC(10, 6),
            duration_ms   INTEGER,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_llm_usage_created_at
            ON llm_usage (created_at DESC)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_llm_usage_provider_model
            ON llm_usage (provider, model)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS llm_usage")
