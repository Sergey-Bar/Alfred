"""Add indexes to request_logs and token_transfers

Revision ID: 004
Revises: 003
Create Date: 2026-02-12 12:00:00.000000
"""
import sqlmodel  # noqa
from alembic import op

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create indexes for dashboard and query performance
    # High-cardinality filter columns (P1 optimization)
    op.create_index(op.f('ix_token_transfers_created_at'), 'token_transfers', ['created_at'], unique=False)

    # Composite index for common query patterns
    op.create_index('ix_request_logs_user_created', 'request_logs', ['user_id', 'created_at'], unique=False)

    # CRITICAL: Add index for API key authentication (used on every request)
    op.create_index('idx_user_api_key_hash', 'users', ['api_key_hash'], unique=False)

    # Additional performance indexes for common queries
    op.create_index('idx_team_member_link_user', 'team_member_links', ['user_id'], unique=False)
    op.create_index('idx_approval_status_created', 'approval_requests', ['status', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_approval_status_created', table_name='approval_requests')
    op.drop_index('idx_team_member_link_user', table_name='team_member_links')
    op.drop_index('idx_user_api_key_hash', table_name='users')
    op.drop_index('ix_request_logs_user_created', table_name='request_logs')
    op.drop_index(op.f('ix_token_transfers_created_at'), table_name='token_transfers')
