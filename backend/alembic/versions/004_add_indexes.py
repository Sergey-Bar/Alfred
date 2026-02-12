"""Add indexes to request_logs and token_transfers

Revision ID: 004
Revises: 003
Create Date: 2026-02-12 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel  # noqa


# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create indexes for dashboard performance
    op.create_index(op.f('ix_request_logs_created_at'), 'request_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_token_transfers_created_at'), 'token_transfers', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_token_transfers_created_at'), table_name='token_transfers')
    op.drop_index(op.f('ix_request_logs_created_at'), table_name='request_logs')
